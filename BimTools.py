from scipy.spatial import Delaunay
from typing import Sequence, Union
from uuid import UUID

from BimDataModel import BBuilding, BBuildElement, BPoint, BSign, mapping_building

NDIGITS:int = 4

class Bim:

    def __init__(self, bim:BBuilding) -> None:
        self.zones = {}
        self.transits = {}

        self._area = 0.0
        self._num_of_people = 0.0
        self._sz_output = []

        for l in bim.levels:
            for e in l.elements:
                element:Union[Zone, Transit]
                if e.sign == BSign.Room or e.sign == BSign.Staircase:
                    element = Zone(e)
                    self._area += element.area
                    self._num_of_people += element.num_of_people
                    self.zones[e.id] = element
                elif e.sign == BSign.DoorWay or e.sign == BSign.DoorWayInt or e.sign == BSign.DoorWayOut:
                    element = Transit(e)
                    self.transits[e.id] = element
                    if len(element.output) == 1:
                        self._sz_output.append(e.id)

        incorrect_transits = []
        t: Transit # for typing the variable
        for t in self.transits.values():
            z_linked:Zone = self.zones[t.output[0]]
            # TODO Calculate the width for transits of type DoorWay
            if not (t.sign == BSign.DoorWayOut) and t.sign == BSign.DoorWay:
                if z_linked.sign == BSign.Staircase and self.zones[t.output[1]].sign == BSign.Staircase:
                    continue
            
            is_successful = t.calculate_width(z_linked)
            if not is_successful:
                incorrect_transits.append((t, z_linked))

        if len(incorrect_transits) > 0:
            import inspect
            from types import FrameType
            frame: Union[FrameType, None] = inspect.currentframe()
            print(f">TransitGeometryException[{__file__}:{frame.f_lineno if not (frame is None) else ()}]. Please check next transits:")
            for t, z in incorrect_transits:
                print(f"{t.sign.name}({t.id}), Zone({z.id}, name={z.name})")
                
            print(">>QGIS expression for find incorrect transits (use 'Select Features Using Expression'):")
            print(' or '.join(f'id is \'{t.id}\'' for t, _ in incorrect_transits))
            print("How to find a bad transition in QGIS:\n \
    1) select layer doorNN\n \
    2) open the attributes table \n \
    3) click to select features using an expression \n \
    4) enter expression: id is 'uuid'. Example: id is '9b9e7724-a021-4099-9dfe-c9b04fdf64ee' \n \
    5) click the right-bottom button 'Select features'")
            exit()

        self._init_safety_zone()
        self.zones[self.safety_zone.id] = self.safety_zone
            
    @property
    def num_of_people(self) -> float:
        return self._num_of_people

    @property
    def area(self) -> float:
        return self._area
    
    @property
    def safety_zone(self) -> 'Zone':
        return self._safety_zone

    def _init_safety_zone(self):
        e = BBuildElement(UUID('e6315dac-ad4b-11ed-9732-d36b774c66a1'), BSign.Room, self._sz_output, 
                          [BPoint(0, 0), BPoint(1000, 0), BPoint(1000, 1000), BPoint(0, 1000), BPoint(0, 0)], 'Safety zone')
        self._safety_zone = Zone(e)

    

class Transit(BBuildElement):

    def __init__(self, build_element:BBuildElement) -> None:
        super().__init__(build_element.id, build_element.sign, build_element.output, build_element.points, build_element.name, build_element.sizeZ)

        self.potential = 0.0
        self.num_of_people = 0.0
        self.is_visited = False
        self.is_blocked = False
        self.is_safe = False
    
    @property
    def width(self) -> float:
        return self._width
    
    @width.setter
    def width(self, w: float) -> None:
        if w <= 0.0:
            raise ValueError("Width of transit below or equal 0 is not possible")
        self._width = w

    def calculate_width(self, zone_element:BBuildElement) -> bool:
        transit_points = [[p.x, p.y] for p in self.points[:-1]]
        zone_points = [[p.x, p.y] for p in zone_element.points[:-1]]
        zone_tri = Delaunay(zone_points)

        edge_points = [i for i, p in enumerate(transit_points) if self._point_in_polygon(p, zone_tri)]
        edge_points.sort(reverse=True)
        
        if not (len(edge_points) == 2):
            return False
        
        p1 = transit_points.pop(edge_points[0])
        p2 = transit_points.pop(edge_points[1])
        p3 = transit_points.pop(1)
        p4 = transit_points.pop(0)

        length = lambda p1, p2: pow(pow(p2[0] - p1[0], 2) + pow(p2[1] - p1[1], 2), 0.5)

        self._width = round((length(p1, p2) + length(p3, p4))/2, NDIGITS)

        return True
        

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
        return f"Transit(name:{self.name})"

class Zone(BBuildElement):

    def __init__(self, build_element:BBuildElement) -> None:
        super().__init__(build_element.id, build_element.sign, build_element.output, build_element.points, build_element.name, build_element.sizeZ)
       
        self._calculate_area()

        self.potential = 0.0
        self.num_of_people = 0.0
        self.is_visited = False
        self.is_blocked = False
        self.is_safe = False
        self.graph_level = 0

    @property
    def area(self) -> float:
        return self._area
    
    def _calculate_area(self):
        def triangle_area(p1, p2, p3) -> float:
            return abs(0.5 * ((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])))

        self._tri = Delaunay([[p.x, p.y] for p in self.points[:-1]])
        self._area = round(sum(triangle_area(self._tri.points[tr[0]], self._tri.points[tr[1]], self._tri.points[tr[2]]) for tr in self._tri.simplices), NDIGITS)

    @property
    def num_of_people(self) -> float:
        return self._num_of_people
    
    @num_of_people.setter
    def num_of_people(self, n: float) -> None:
        if n < 0:
            raise ValueError("Number of people in zone below 0 is not possible")
        self._num_of_people = n

    def __repr__(self) -> str:
        return f"Zone(name:{self.name})"
    
    def __hash__(self):
        return hash(self.id)


# Tests
if __name__ == "__main__":
    building = mapping_building('resources/building_example.json')
    # Test Zone
    print('Zone test')
    be1 = building.levels[0].elements[1]
    z1 = Zone(be1)
    print(z1.area)

    # for l in building.levels:
    #     for e in l.elements:
    #         z1 = Zone(e)
    #         print(z1.get_area())

    # Test Transit
    print('Transit test')
    # z1: Zone
    be1 = list(filter(lambda be: be.id == UUID("4199e3d7-5f08-4aab-8997-3b7cb1cd8cd8"), building.levels[0].elements))[0]
    t1: Transit = Transit(list(filter(lambda be: be.id == UUID("f46361f4-a99f-4e79-aebe-d36ebed45992"), building.levels[0].elements))[0])

    print(z1)
    print(t1)
    t1.calculate_width(be1)
    print(t1.width)


    # Test Bim
    print('== BIM test ==')
    bim = Bim(building)
    v:Transit
    for k, v in bim.transits.items():
        print(k, v.width)
    
    print(bim.safety_zone.area)