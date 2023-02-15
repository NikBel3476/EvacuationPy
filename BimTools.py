from scipy.spatial import Delaunay
from typing import Sequence

from BimDataModel import BBuilding, BBuildElement, BPoint, BSign, mapping_building

NDIGITS:int = 4

class Bim:

    def __init__(self, bim:BBuilding) -> None:
        self.list_of_elements = {}

        for l in bim.levels:
            for e in l.elements:
                element = None
                if e.sign == BSign.Room or e.sign == BSign.Staircase:
                    element = Zone(e)
                elif e.sign == BSign.DoorWay or e.sign == BSign.DoorWayInt or e.sign == BSign.DoorWayOut:
                    element = Transit(e)
                self.list_of_elements[e.id] = element


    def get_num_of_people(self) -> float:
        return 0.0

    def set_num_of_people(self) -> None:
        pass

    def get_area(self) -> float:
        return 0.0


class Polygon:
    def __init__(self, points: list) -> None:
        pass

class Transit(BBuildElement):

    def __init__(self, build_element:BBuildElement) -> None:
        self.width = 0.0
        self._build_element = build_element
    
    @property
    def width(self) -> float:
        return self._width
    
    @width.setter
    def width(self, w: float) -> None:
        if w <= 0.0:
            raise ValueError("Width of transit below or equal 0 is not possible")
        self._width = w

    def calculate_width(self, zone_element:BBuildElement) -> None:
        transit_points = [[p.x, p.y] for p in self._build_element.points[:-1]]
        zone_points = [[p.x, p.y] for p in zone_element.points[:-1]]
        zone_tri = Delaunay(zone_points)

        edge_points = [i for i, p in enumerate(transit_points) if self._point_in_polygon(p, zone_tri)]
        edge_points.sort(reverse=True)
        
        p1 = transit_points.pop(edge_points[0])
        p2 = transit_points.pop(edge_points[1])
        p3 = transit_points.pop(1)
        p4 = transit_points.pop(0)

        length = lambda p1, p2: pow(pow(p2[0] - p1[0], 2) + pow(p2[1] - p1[1], 2), 0.5)

        self._width = round((length(p1, p2) + length(p3, p4))/2, NDIGITS)
        # print(edge_points, self._width)
        

    def _point_in_polygon(self, point, zone_tri:Delaunay) -> bool:
        '''
        Проверка вхождения точки в прямоугольник

        Для этого произвоится треангуляция прямоугольника. В данном случае треангуляция осуществляется вручную,
        потому что нам известно, что каждое помещение представляет прямоугольником.
        После получения треугольников поподает ли точка в треугольник, для чего выполняется проверка 
        с какой стороны от стороны треугольника находится точка.
        '''
        
        def where_point(a, b, p) -> int:
            '''
            Проверка с какой стороны находится точка \n
            a, b, p - точки, представленные массивом [x, y] \n
            ab - вектор \n
            p - точка 
            '''
            s = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
            if s > 0: return 1        # Точка слева от вектора AB
            elif s < 0: return -1     # Точка справа от вектора AB
            else: return 0            # Точка на векторе, прямо по вектору или сзади вектора

        def is_point_in_triangle(triangle:list, p) -> bool:
            '''
            Проверка попадания точки в треугольник \n
            triangle - треугольник, представленный массивом [[x, y], [x, y], [x, y]] \n
            p - точка, представленная массивом [x, y] \n
            '''
            q1 = where_point(triangle[0], triangle[1], p)
            q2 = where_point(triangle[1], triangle[2], p)
            q3 = where_point(triangle[2], triangle[0], p)
            return q1 >= 0 and q2 >= 0 and q3 >= 0
        
        '''
        Проверяем в какие треугольники попадает точка
        '''
        for tr in zone_tri.simplices:
            if is_point_in_triangle([zone_tri.points[tr[0]], zone_tri.points[tr[1]], zone_tri.points[tr[2]]], point):
                break
        else: # В это условие попадаем, если прошли цикл
            return False
        
        return True
    
    def __repr__(self) -> str:
        return f"Transit(name:{self._build_element.name})"

class Zone(BBuildElement):

    def __init__(self, build_element:BBuildElement) -> None:
        self._area = 0.0
        self._points = [[p.x, p.y] for p in build_element.points[:-1]]
        self._num_of_people = 0.0
        self._build_element = build_element

    def get_area(self) -> float:
        def triangle_area(p1, p2, p3) -> float:
            return abs(0.5 * ((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])))

        if self._area == 0.0:
            self._tri = Delaunay(self._points)
            self._area = round(sum(triangle_area(self._tri.points[tr[0]], self._tri.points[tr[1]], self._tri.points[tr[2]]) for tr in self._tri.simplices), NDIGITS)
        
        return self._area

    def get_num_of_people(self) -> float:
        return self._num_of_people
    
    def set_num_of_people(self, n: float) -> None:
        self._num_of_people += n

    def __repr__(self) -> str:
        return f"Zone(name:{self._build_element.name})"


# Tests
if __name__ == "__main__":
    building = mapping_building('resources/building_example.json')
    # Test Zone
    print('Zone test')
    be1 = building.levels[0].elements[1]
    z1 = Zone(be1)
    print(z1.get_area())

    # for l in building.levels:
    #     for e in l.elements:
    #         z1 = Zone(e)
    #         print(z1.get_area())

    # Test Transit
    print('Transit test')
    from uuid import UUID
    # z1: Zone
    t1: Transit
    for l in building.levels:
        be1 = list(filter(lambda be: be.id == UUID("4199e3d7-5f08-4aab-8997-3b7cb1cd8cd8"), l.elements))[0]
        t1 = Transit(list(filter(lambda be: be.id == UUID("f46361f4-a99f-4e79-aebe-d36ebed45992"), l.elements))[0])
        break

    print(z1)
    print(t1)
    t1.calculate_width(be1)
    print(t1.width)


    # Test Bim
    print('== BIM test ==')
    bim = Bim(building)
    for k, v in bim.list_of_elements.items():
        print(k, v)