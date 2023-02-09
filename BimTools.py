from scipy.spatial import Delaunay
from typing import Sequence
from BimDataModel import BBuildElement, BPoint, mapping_building

NDIGITS:int = 4

class Bim:

    def get_num_of_people(self) -> float:
        return 0.0

    def set_num_of_people(self) -> None:
        pass

    def get_area(self) -> float:
        return 0.0


class Transit:

    def __init__(self) -> None:
        self._width = 0

    def get_width(self) -> float:
        return 0.0
    
    def set_width(self) -> None:
        pass

class Zone:

    def __init__(self, build_element:BBuildElement) -> None:
        self._area:float = 0.0
        self._points = [[p.x, p.y] for p in build_element.points[:-1]]
        self._num_of_people = 0.0

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


# Tests
if __name__ == "__main__":
    # Test Zone
    building = mapping_building('resources/building_example.json')
    print('Zone test')
    be1 = building.levels[0].elements[1]
    z1 = Zone(be1)

    for l in building.levels:
        for e in l.elements:
            z1 = Zone(e)
            print(z1.get_area())

