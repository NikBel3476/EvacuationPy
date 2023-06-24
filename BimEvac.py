from BimDataModel import BSign
from BimTools import Bim, Transit, Zone
from uuid import UUID
from typing import Set, Tuple, Dict, List

import math
import matplotlib.pyplot as plt


class PeopleFlowVelocity(object):
    ROOM, TRANSIT, STAIR_UP, STAIR_DOWN = range(4)
    V0, A, D0 = range(3)
    PATH_VALUE = {
        ROOM: [100, 0.295, 0.51],
        TRANSIT: [100, 0.295, 0.65],
        STAIR_DOWN: [100, 0.400, 0.89],
        STAIR_UP: [60, 0.305, 0.67],
    }

    def __init__(self, projection_area: float = 0.1) -> None:
        self.projection_area = projection_area
        self.D09 = self.to_pm2(0.9)

    def to_m2m2(self, d: float) -> float:
        return d * self.projection_area

    def to_pm2(self, D: float) -> float:
        return D / self.projection_area

    @staticmethod
    def velocity(v0: float, a: float, d0: float, d: float) -> float:
        """
        Функция скорости. Базовая зависимость, которая позволяет определить скорость людского
        потока по его плотности

        Parameters
        ----------
        v0 : float
            начальная скорость потока, м./мин.
        a : float
            коэффициент вида пути
        d0 : float
            допустимая плотность людского потока на участке, чел./м2
        d : float
            текущая плотность людского потока на участке, чел./м2

        Return
        ------
        Скорость людского потока, м/мин
        """

        return v0 * (1.0 - a * math.log(d / d0))

    def speed_through_transit(self, width: float, d: float) -> float:
        """
        Функция скорости движения людского потока через проем

        Parameters
        ----------
        width : float
            ширина проема
        d : float
            плотность людского потока в элементе, для которого определяется скорость

        Return
        ------
        Скорость, м/мин
        """

        v0 = PeopleFlowVelocity.PATH_VALUE[PeopleFlowVelocity.TRANSIT][PeopleFlowVelocity.V0]
        d0 = PeopleFlowVelocity.PATH_VALUE[PeopleFlowVelocity.TRANSIT][PeopleFlowVelocity.D0]
        a = PeopleFlowVelocity.PATH_VALUE[PeopleFlowVelocity.TRANSIT][PeopleFlowVelocity.A]

        if d > d0:
            D = d * self.projection_area

            m = 1 if D <= 0.5 else 1.25 - 0.5 * D
            q = PeopleFlowVelocity.velocity(v0, a, d0, d) * D * m

            if D >= 0.9:
                q = 2.5 + 3.75 * width if width < 1.6 else 8.5

            v0 = q / D

        return v0

    def speed_in_room(self, d: float) -> float:
        """
        Parameters
        ----------
        d : float
            плотность людского потока в элементе, для которого определяется скорость

        Return
        ------
        Скорость потока по горизонтальному пути, м/мин
        """
        # Если плотность потока более 0.9 м2/м2,
        # то принудительно устанавливаем ее на уровке 0.9 м2/м2
        d = self.D09 if d >= self.D09 else d

        v0 = PeopleFlowVelocity.PATH_VALUE[PeopleFlowVelocity.ROOM][PeopleFlowVelocity.V0]
        d0 = PeopleFlowVelocity.PATH_VALUE[PeopleFlowVelocity.ROOM][PeopleFlowVelocity.D0]
        a = PeopleFlowVelocity.PATH_VALUE[PeopleFlowVelocity.ROOM][PeopleFlowVelocity.A]

        return PeopleFlowVelocity.velocity(v0, a, d0, d) if d > d0 else v0

    def speed_on_stair(self, direction: int, d: float) -> float:
        # Если плотность потока более 0.9 м2/м2,
        # то принудительно устанавливаем ее на уровке 0.9 м2/м2
        d = self.D09 if d >= self.D09 else d

        if not (direction == PeopleFlowVelocity.STAIR_DOWN or direction == PeopleFlowVelocity.STAIR_UP):
            raise ValueError(
                f"Некорректный индекс направления движеия по лестнице: {direction}. \n\
                               Индекс можети принимать значение `PeopleFlowVelocity.STAIR_DOWN` или `PeopleFlowVelocity.STAIR_UP`"
            )

        v0 = PeopleFlowVelocity.PATH_VALUE[direction][PeopleFlowVelocity.V0]
        d0 = PeopleFlowVelocity.PATH_VALUE[direction][PeopleFlowVelocity.D0]
        a = PeopleFlowVelocity.PATH_VALUE[direction][PeopleFlowVelocity.A]

        return PeopleFlowVelocity.velocity(v0, a, d0, d) if d > d0 else v0


class Moving(object):
    MODELLING_STEP = 0.008  # мин.
    MIN_DENSIY = 0.1  # чел./м2
    MAX_DENSIY = 5.0  # чел./м2

    def __init__(self) -> None:
        self.pfv = PeopleFlowVelocity(projection_area=0.1)
        self._step_counter = [0, 0, 0]
        self.direction_pairs: Dict[UUID, Tuple[Zone, Zone]] = {}

    def step(self, bim: Bim):
        self._step_counter[0] += 1
        for t in bim.transits.values():
            t.is_visited = False
        for z in bim.zones.values():
            z.is_visited = False

        zones_to_process: Set[Zone] = set([bim.safety_zone])
        receiving_zone: Zone = zones_to_process.pop()

        self._step_counter[1] = 0

        while True:
            self._step_counter[2] = 0
            transit: Transit
            for transit in (bim.transits[tid] for tid in receiving_zone.output):
                if transit.is_visited or transit.is_blocked:
                    continue

                giving_zone: Zone = bim.zones[transit.output[0]]
                if giving_zone.id == receiving_zone.id:
                    giving_zone = bim.zones[transit.output[1]]

                # giving_zone.potential = self.potential(receiving_zone, giving_zone, transit.width)
                moved_people = self.part_of_people_flow(receiving_zone, giving_zone, transit)

                receiving_zone.num_of_people += moved_people
                giving_zone.num_of_people -= moved_people
                transit.num_of_people = moved_people
                self.direction_pairs[transit.id] = (giving_zone, receiving_zone)

                giving_zone.is_visited = True
                transit.is_visited = True

                if len(giving_zone.output) > 1:  # отсекаем помещения, в которых одна дверь
                    zones_to_process.add(giving_zone)

                self._step_counter[2] += 1

            if len(zones_to_process) == 0:
                break

            receiving_zone = zones_to_process.pop()

            self._step_counter[1] += 1

    def potential(self, rzone: Zone, gzone: Zone, twidth: float) -> float:
        p = math.sqrt(gzone.area) / self.speed_at_exit(rzone, gzone, twidth)
        return rzone.potential + p

    def speed_at_exit(self, rzone: Zone, gzone: Zone, twidth: float) -> float:
        # Определение скорости на выходе из отдающего помещения
        zone_speed = self.speed_in_element(rzone, gzone)
        transition_speed = self.pfv.speed_through_transit(twidth, gzone.density)

        return min(zone_speed, transition_speed)

    def speed_in_element(self, rzone: Zone, gzone: Zone) -> float:
        # По умолчанию, используется скорость движения по горизонтальной поверхности
        v_zone = self.pfv.speed_in_room(gzone.density)

        dh = rzone.points[0].z - gzone.points[0].z  # Разница высот зон
        # Если принимающее помещение является лестницей и находится на другом уровне,
        # то скорость будет рассчитываться как по наклонной поверхности
        if abs(dh) > 1e-3 and rzone.sign == BSign.Staircase:
            """Иначе определяем направление движения по лестнице
                     ______   aGiverItem
                   //                         => direction = STAIR_UP
                  //
            _____//           aReceivingItem
                 \\
                  \\                          => direction = STAIR_DOWN
                   \\______   aGiverItem
            """
            direction: int = self.pfv.STAIR_DOWN if dh > 0 else self.pfv.STAIR_UP
            v_zone = self.pfv.speed_on_stair(direction, gzone.density)

        return v_zone

    def part_of_people_flow(self, rzone: Zone, gzone: Zone, transit: Transit) -> float:
        # density_min_giver_zone = 0.5 / area_giver_zone
        min_density_gzone = self.MIN_DENSIY  # if self.MIN_DENSIY > 0 else self.pfv.projection_area * 0.5 / gzone.area

        # Ширина перехода между зонами зависит от количества человек,
        # которое осталось в помещении. Если там слишком мало людей,
        # то они переходя все сразу, чтоб не дробить их
        door_width = transit.width if gzone.density > min_density_gzone else gzone.area  # transit.width
        speedatexit = self.speed_at_exit(rzone, gzone, door_width)

        # Кол. людей, которые могут покинуть помещение за шаг моделирования
        part_of_people_flow = self.change_numofpeople(gzone, door_width, speedatexit)
        if gzone.density <= min_density_gzone:
            if part_of_people_flow > gzone.num_of_people:
                print("===WTF!===")
            part_of_people_flow = gzone.num_of_people

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
        if capacity_reciving_zone < 0:
            return 0.0
        else:
            return part_of_people_flow if (capacity_reciving_zone > part_of_people_flow) else capacity_reciving_zone

    def change_numofpeople(self, gzone: Zone, twidth: float, speed_at_exit: float) -> float:
        # Величина людского потока, через проем шириной twidth, чел./мин
        P = gzone.density * speed_at_exit * twidth
        # Зная скорость потока, можем вычислить конкретное количество человек,
        # которое может перейти в принимющую зону (путем умножения потока на шаг моделирования)
        return P * self.MODELLING_STEP


if __name__ == "__main__":
    # print(PeopleFlowVelocity.velocity(1,1,1,1))
    debug = False
    if debug:
        print("Test of PeopleFlowVelocity")
        print("--------------------------")
        pfv = PeopleFlowVelocity()
        D = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        print(f"Density:{D}")
        # D = [0.1, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        print("#ROOMS")
        V = [100, 100, 80.14, 59.69, 47.73, 39.24, 32.66, 27.28, 22.73, 18.79, 15.32, 15.32]
        # Q = [1.0, 5.0, 8.0, 12.0, 14.1, 16.0, 16.5, 16.3, 16.1, 15.2, 13.5, 13.5]

        vals: List[float] = []
        q: List[float] = []
        for d0 in D:
            v = round(pfv.speed_in_room(pfv.to_pm2(d0)), 2)
            vals.append(v)
            # q.append(round(v * d0, 1))

        print("-----")
        print(f"Origin: {V}")
        print(f"Rintd : {vals}")
        print("-----")
        # print(f'Origin: {Q}')
        # print(f'Rintd : {q}')

        print("#DOORS")
        D1 = [0.5, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59, 0.6]
        V1 = [39.82, 38.25, 37.50, 36.75, 36.04, 35.35, 34.64, 33.96, 33.31, 32.66, 32.02]

        V = [  # pyright: ignore [reportConstantRedefinition]
            100,
            100,
            87.30,
            66.85,
            54.87,
            46.40,
            39.82,
            32.02,
            26.30,
            21.54,
            9.44,
            9.44,
        ]
        Q = [1.0, 5.0, 8.7, 13.4, 16.5, 18.4, 19.6, 19.05, 18.5, 17.3, 8.5, 8.5]

        vals = []
        q = []
        for d0 in D:
            v = round(pfv.speed_through_transit(1.6, pfv.to_pm2(d0)), 2)
            vals.append(v)
            q.append(round(v * d0, 1))

        print(f"Origin: {V}")
        print(f"Rintd : {vals}")
        print("-----")
        # print(f'Origin: {Q}')
        # print(f'Rintd : {q}')

        # plot
        # fig, ax = plt.subplots()

        # ax.plot(D, V, linewidth=2.0, label='Original')
        # ax.plot(D, vals, linewidth=2.0, label='My')

        # # Adding legend, which helps us recognize the curve according to it's color
        # plt.legend()
        # plt.show()

        print("#STAIRS")
        V = {  # pyright: ignore [reportConstantRedefinition]
            pfv.STAIR_UP: [60.00, 60.00, 52.67, 39.99, 32.57, 27.30, 23.22, 19.88, 17.06, 14.62, 12.46, 12.46],
            pfv.STAIR_DOWN: [100.0, 100.00, 95.30, 67.60, 51.40, 39.88, 30.96, 23.67, 17.50, 12.16, 7.44, 7.44],
        }

        vals = []
        for d0 in D:
            v = round(pfv.speed_on_stair(pfv.STAIR_DOWN, pfv.to_pm2(d0)), 2)
            vals.append(v)

        print(f"Origin: {V[pfv.STAIR_DOWN]} DOWN")
        print(f"Rintd : {vals}")
        print("-----")

        vals = []
        for d0 in D:
            v = round(pfv.speed_on_stair(pfv.STAIR_UP, pfv.to_pm2(d0)), 2)
            vals.append(v)

        print(f"Origin: {V[pfv.STAIR_UP]} UP")
        print(f"Rintd : {vals}")
        print("-----")

        exit(0)

    import BimDataModel
    from BimTools import Bim
    from BimComplexity import BimComplexity

    # building = BimDataModel.mapping_building('resources/example-one-exit.json')
    building = BimDataModel.mapping_building("resources/example-two-exits.json")
    # TODO: replace absolute path to relative
    building = BimDataModel.mapping_building(
        r"/home/boris/Documents/teaching/УдГУ/Рабочие_программы/2022-2023/Прототипирование СБ 1 курс/qgis/Тестовые задачи/test01/test01.2.json"
    )
    # building = BimDataModel.mapping_building('resources/building_example.json')

    bim = Bim(building)
    BimComplexity(bim)  # check a building

    z: Zone
    t: Transit
    wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

    # Doors width
    for t in bim.transits.values():
        t.width = 2.0
        # print(f"{t.name} -- {t.width}")

    density = 1.0
    # for z in wo_safety:
    #     # if '5c4f4' in str(z.id):
    #     # if '7e466' in str(z.id) or '02707' in str(z.id):
    #     z.num_of_people = density * z.area

    D = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # м2/м2 # pyright: ignore [reportConstantRedefinition]
    T = [15.0, 20.0, 25.5, 30.0, 36.4, 42.9, 52.2, 63.2, 80.0]  # сек.

    times: List[float] = []  # сек.

    for density in D:
        m = Moving()

        bim.set_density(m.pfv.to_pm2(density))

        num_of_people = 0.0
        for z in wo_safety:
            # print(z.num_of_people)
            num_of_people += z.num_of_people

        # for z in bim.zones.values():
        #     print(f"{z}, Potential: {z.potential}, Number of people: {z.num_of_people}, Density: {z.density}")

        time = 0.0
        for _ in range(10000):
            m.step(bim)
            print(m.direction_pairs)
            time += Moving.MODELLING_STEP
            # for z in bim.zones.values():
            #     print(f"{z}, Potential: {z.potential}, Number of people: {z.num_of_people}")
            for t in bim.transits.values():
                if t.sign == BSign.DoorWayOut:
                    pass
                    # print(f"{t}, Number of people: {t.num_of_people}")

            nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
            # if nop < 10e-3:
            if nop <= 0:
                break
        else:
            print("# Error! ", end="")

            # print("========", nop, bim.safety_zone.num_of_people)

        print(f"Количество человек: {num_of_people:.{4}} Длительность эвакуации: {time*60:.{4}} с. ({time:.{4}} мин.)")
        nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
        times.append(round(time * 60, 1))
        # print("========", nop, bim.safety_zone.num_of_people)

    print(D)
    print(T)
    print(times)

    p: List[float] = []
    for i in range(len(T)):
        p.append(round(T[i] / times[i], 2))

    print(p)

    # plot
    fig, ax = plt.subplots()  # pyright: ignore [reportUnknownMemberType]

    ax.plot(D, T, linewidth=2.0, label="Original")  # pyright: ignore [reportUnknownMemberType]
    ax.plot(D, times, linewidth=2.0, label="My")  # pyright: ignore [reportUnknownMemberType]

    # Adding legend, which helps us recognize the curve according to it's color
    plt.legend()  # pyright: ignore [reportUnknownMemberType]
    plt.show()  # pyright: ignore [reportUnknownMemberType]
