import BimDataModel
from BimTools import Bim, Transit, Zone
import math

class PeopleFlow(object):
    
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
            v0k = PeopleFlow.velocity(v0, a, density_in_zone, d0) * m

            if (density_in_zone >= 9 and transit_width < 1.6):
                v0k = 10 * (2.5 + 3.75 * transit_width) / d0
        else:
            v0k = v0

        if (v0k < 0):
            raise ValueError("People flow speed less 0")

        return v0k

    @staticmethod
    def speed_in_room(density_in_zone:float, v_max:float) -> float:
        '''density_in_zone - плотность в элементе, из которого выходит поток

        return Скорость потока по горизонтальному пути, м/мин'''

        v0 = v_max # м/мин
        d0 = 0.51
        a = 0.295

        return PeopleFlow.velocity(v0, a, density_in_zone, d0) if density_in_zone > d0 else v0

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

        return PeopleFlow.velocity(v0, a, density_in_zone, d0) if density_in_zone > d0 else v0


def evac_step(bim:Bim):
    zones_to_process = set()
    receiving_zone = bim.safety_zone

    while True:
        transit: Transit
        for transit in (bim.transits[tid] for tid in receiving_zone.output):
            if transit.is_visited or transit.is_blocked:
                continue

            giving_zone: Zone = bim.zones[transit.output[0]]
            if giving_zone.id == receiving_zone.id:
                giving_zone = bim.zones[transit.output[1]]
            
            giving_zone.is_visited = True
            transit.is_visited = True

            if len(giving_zone.output) > 1: # отсекаем помещения, в которых одна дверь
                zones_to_process.add(giving_zone)

        receiving_zone = zones_to_process.pop()
        print(receiving_zone, zones_to_process)

        if len(zones_to_process) == 0:
            break




if __name__ == '__main__':
    print(PeopleFlow.velocity(1,1,1,1))