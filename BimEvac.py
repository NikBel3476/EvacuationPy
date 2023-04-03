from functools import reduce
from BimDataModel import BSign
from BimTools import Bim, Transit, Zone
import math

class PeopleFlowVelocity(object):

    MAX_SPEED = 100
    
    @staticmethod
    def velocity(v0:float, a:float, d:float, d0:float) -> float:
        '''Функция скорости. Базовая зависимость, которая позволяет определить скорость людского
        потока по его плотности
        
        v0 - начальная скорость потока\n
        a  - коэффициент вида пути\n
        d  - текущая плотность людского потока на участке, чел./м2\n
        d0 - допустимая плотность людского потока на участке, чел./м2\n
        return скорость, м/мин.'''

        return v0 * (1.0 - a * math.log(d / d0))
    
    @staticmethod
    def speed_through_transit(transit_width:float, density_in_zone:float, v_max:float) -> float:
        v0 = v_max
        d0 = 0.65
        a  = 0.295
        v0k = -1.0

        if density_in_zone > d0:
            m = (1.25 - 0.05 * density_in_zone) if (density_in_zone > 5) else 1
            v0k = PeopleFlowVelocity.velocity(v0, a, density_in_zone, d0) * m

            if (density_in_zone >= 9 and transit_width < 1.6):
                v0k = 10 * (2.5 + 3.75 * transit_width) / d0
        else:
            v0k = v0

        if (v0k < 0):
            raise ValueError("People flow speed less 0")

        return v0k

    @staticmethod
    def speed_in_room(density_in_zone:float) -> float:
        '''density_in_zone - плотность в элементе, из которого выходит поток

        return Скорость потока по горизонтальному пути, м/мин'''

        v0 = PeopleFlowVelocity.MAX_SPEED # м/мин
        d0 = 0.51
        a = 0.295

        return PeopleFlowVelocity.velocity(v0, a, density_in_zone, d0) if density_in_zone > d0 else v0

    @staticmethod
    def speed_on_stair(density_in_zone:float, direction:int) -> float:
        d0 = 0.0
        v0 = 0.0
        a  = 0.0

        if direction > 0:
            d0 = 0.67
            v0 = 50.0
            a  = 0.305
        elif direction < 0:
            d0 = 0.89
            v0 = 80.0
            a  = 0.4
        else:
            raise ValueError("Value of 'direction' equal 0 is not possible")

        return PeopleFlowVelocity.velocity(v0, a, density_in_zone, d0) if density_in_zone > d0 else v0

class Moving(object):

    MODELLING_STEP = 0.01 # min
    MIN_DENSIY = 0.1
    MAX_DENSIY = 5.0
    
    def step(self, bim:Bim):
        for t in bim.transits.values(): t.is_visited = False
        for z in bim.zones.values(): z.is_visited = False

        zones_to_process = set([bim.safety_zone])
        receiving_zone: Zone = zones_to_process.pop()

        while True:
            
            transit: Transit
            for transit in (bim.transits[tid] for tid in receiving_zone.output):
                if transit.is_visited or transit.is_blocked:
                    continue

                giving_zone: Zone = bim.zones[transit.output[0]]
                if giving_zone.id == receiving_zone.id:
                    giving_zone = bim.zones[transit.output[1]]
                
                giving_zone.potential = self.potential(receiving_zone, giving_zone, transit.width)
                moved_people = self.part_of_people_flow(receiving_zone, giving_zone, transit)

                receiving_zone.num_of_people += moved_people
                giving_zone.num_of_people -= moved_people
                transit.num_of_people = moved_people

                giving_zone.is_visited = True
                transit.is_visited = True

                if len(giving_zone.output) > 1: # отсекаем помещения, в которых одна дверь
                    zones_to_process.add(giving_zone)

            if len(zones_to_process) == 0:
                break
            
            receiving_zone = zones_to_process.pop()


    def potential(self, rzone:Zone, gzone:Zone, twidth:float) -> float:
        p = math.sqrt(gzone.area) / self.speed_at_exit(rzone, gzone, twidth)
        return rzone.potential + p
    
    def speed_at_exit(self, rzone:Zone, gzone:Zone, twidth:float) -> float:
        #Определение скорости на выходе из отдающего помещения
        zone_speed = self.speed_in_element(rzone, gzone)
        density_in_giver_element = gzone.num_of_people / gzone.area
        transition_speed = PeopleFlowVelocity.speed_through_transit(twidth, density_in_giver_element, PeopleFlowVelocity.MAX_SPEED)
        
        return min(zone_speed, transition_speed)

    def speed_in_element(self, rzone:Zone, gzone:Zone) -> float:
        density_in_giver_zone = gzone.num_of_people / gzone.area
        # По умолчанию, используется скорость движения по горизонтальной поверхности
        v_zone = PeopleFlowVelocity.speed_in_room(density_in_giver_zone)

        dh = rzone.points[0].z - gzone.points[0].z #Разница высот зон

        # Если принимающее помещение является лестницей и находится на другом уровне,
        # то скорость будет рассчитываться как по наклонной поверхности
        if abs(dh) > 1e-3 and rzone.sign == BSign.Staircase:
            '''Иначе определяем направление движения по лестнице
            -1 вниз, 1 вверх
                    ______   aGiverItem
                   /                         => direction = -1
                  /
            _____/           aReceivingItem
                 \
                  \                          => direction = 1
                   \______   aGiverItem
            '''
            direction:int = -1 if dh > 0 else 1
            v_zone = PeopleFlowVelocity.speed_on_stair(density_in_giver_zone, direction)

        if v_zone < 0:
            raise ValueError(f"Скорость в отдающей зоне меньше 0: {gzone.name}")

        return v_zone

    def part_of_people_flow(self, rzone:Zone, gzone:Zone, transit:Transit) -> float:
        area_giver_zone = gzone.area
        people_in_giver_zone = gzone.num_of_people
        density_in_giver_zone= people_in_giver_zone / area_giver_zone
        # density_min_giver_zone = 0.5 / area_giver_zone
        density_min_giver_zone = self.MIN_DENSIY if self.MIN_DENSIY > 0 else 0.5 / area_giver_zone

        # Ширина перехода между зонами зависит от количества человек,
        # которое осталось в помещении. Если там слишком мало людей,
        # то они переходя все сразу, чтоб не дробить их
        door_width = transit.width; #(densityInElement > densityMin) ? aDoor.VCn().getWidth() : std::sqrt(areaElement);
        speedatexit = self.speed_at_exit(rzone, gzone, door_width)

        # Кол. людей, которые могут покинуть помещение
        part_of_people_flow = self.change_numofpeople(gzone, door_width, speedatexit) \
                                if (density_in_giver_zone > density_min_giver_zone) \
                                else people_in_giver_zone

        # Т.к. зона вне здания принята безразмерной,
        # в нее может войти максимально возможное количество человек
        # Все другие зоны могут принять ограниченное количество человек.
        # Т.о. нужно проверить может ли принимающая зона вместить еще людей.
        # capacity_reciving_zone - количество людей, которое еще может
        # вместиться до достижения максимальной плотности
        # => если может вместить больше, чем может выйти, то вмещает всех вышедших,
        # иначе вмещает только возможное количество.
        max_numofpeople = self.MAX_DENSIY * rzone.area
        capacity_reciving_zone = max_numofpeople - rzone.num_of_people
        # Такая ситуация возникает при плотности в принимающем помещении более Dmax чел./м2
        # Фактически capacity_reciving_zone < 0 означает, что помещение не может принять людей
        if capacity_reciving_zone < 0: return 0.0
        else: return part_of_people_flow if (capacity_reciving_zone > part_of_people_flow) else capacity_reciving_zone

    def change_numofpeople(self, gzone:Zone, twidth:float, speed_at_exit:float) -> float:
        densityInElement = gzone.num_of_people / gzone.area
        # Величина людского потока, через проем шириной aWidthDoor, чел./мин
        P = densityInElement * speed_at_exit * twidth
        # Зная скорость потока, можем вычислить конкретное количество человек,
        # которое может перейти в принимющую зону (путем умножения потока на шаг моделирования)
        return P * self.MODELLING_STEP


if __name__ == '__main__':
    # print(PeopleFlowVelocity.velocity(1,1,1,1))
    import BimDataModel
    from BimTools import Bim
    from BimComplexity import BimComplexity
    from BimEvac import Moving

    # building = BimDataModel.mapping_building('resources/example-one-exit.json')
    building = BimDataModel.mapping_building('resources/example-two-exits.json')
    # building = BimDataModel.mapping_building('resources/building_example.json')

    bim = Bim(building)
    BimComplexity(bim) # check a building

    z: Zone
    t: Transit
    wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

    # Doors width
    for t in bim.transits.values():
        print(f"{t.name} -- {t.width}")

    density = 1
    for z in wo_safety:
        # if '5c4f4' in str(z.id):
        # if '7e466' in str(z.id) or '02707' in str(z.id):
        z.num_of_people = density * z.area

    for z in wo_safety:
        print(z.num_of_people)

    m = Moving()

    for z in bim.zones.values(): print(f"{z}, Potential: {z.potential}, Number of people: {z.num_of_people}")

    time = 0.0
    for _ in range(1000):
        m.step(bim)
        time += Moving.MODELLING_STEP
        # for z in bim.zones.values():
        #     print(f"{z}, Potential: {z.potential}, Number of people: {z.num_of_people}")
        for t in bim.transits.values():
            if t.sign == BSign.DoorWayOut:
                print(f"{t}, Number of people: {t.num_of_people}")

        nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
        # if nop < 10e-3:
        if nop <= 0:
            break
        
        print("========", nop, bim.safety_zone.num_of_people)
    
    print(f'Длительность эвакуации: {time*60:.{4}} с. ({time:.{4}} мин.)')
    nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
    # print("========", nop, bim.safety_zone.num_of_people)