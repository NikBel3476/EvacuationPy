from dataclasses import dataclass

from typing import Union, Tuple, List, Dict
from uuid import UUID
import tripy
import math
from BimDataModel import BBuilding, BBuildElement, BPoint, BSign, mapping_building

Point2D = Tuple[float, float]
Triangle = Tuple[Point2D, Point2D, Point2D]
Triangles = List[Triangle]

NDIGITS: int = 15


class Bim:
    def __init__(self, bim: BBuilding) -> None:
        self.zones: Dict[UUID, Zone] = {}
        self.transits: Dict[UUID, Transit] = {}

        self._area = 0.0
        self._num_of_people = 0.0
        self._sz_output: List[UUID] = []

        for level in bim.levels:
            for e in level.elements:
                element: Union[Zone, Transit]
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

        incorrect_transits: List[Tuple[Transit, Zone]] = []
        for t in self.transits.values():
            z_linked: Zone = self.zones[t.output[0]]
            # TODO Calculate the width for transits of type DoorWay
            if not (t.sign == BSign.DoorWayOut) and t.sign == BSign.DoorWay:
                if z_linked.sign == BSign.Staircase and self.zones[t.output[1]].sign == BSign.Staircase:
                    continue

            if not t.calculate_width(z_linked, self.zones[t.output[1]] if len(t.output) > 1 else None):
                incorrect_transits.append((t, z_linked))

        if len(incorrect_transits) > 0:
            import inspect
            from types import FrameType

            frame: Union[FrameType, None] = inspect.currentframe()
            print(
                f">TransitGeometryException[{__file__}:{frame.f_lineno if frame is not None else ()}]. Please check next transits:"
            )
            for t, z in incorrect_transits:
                print(f"{t.sign.name}({t.id}), Zone({z.id}, name={z.name})")

            print(">>QGIS expression for find incorrect transits (use 'Select Features Using Expression'):")
            print(" or ".join(f"id is '{t.id}'" for t, _ in incorrect_transits))
            print(
                "How to find a bad transition in QGIS:\n \
    1) select layer doorNN\n \
    2) open the attributes table \n \
    3) click to select features using an expression \n \
    4) enter expression: id is 'uuid'. Example: id is '9b9e7724-a021-4099-9dfe-c9b04fdf64ee' \n \
    5) click the right-bottom button 'Select features'"
            )
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
    def safety_zone(self) -> "Zone":
        return self._safety_zone

    def _init_safety_zone(self):
        import sys

        s = sys.float_info.max**0.2
        e = BBuildElement(
            UUID("e6315dac-ad4b-11ed-9732-d36b774c66a1"),
            BSign.Room,
            self._sz_output,
            [
                BPoint(0, 0),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(s, 0),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(s, s),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(0, s),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(0, 0),  # pyright: ignore [reportGeneralTypeIssues]
            ],
            "Safety zone",
        )
        self._safety_zone = Zone(e)

    def set_density(self, value: float) -> None:
        z: Zone
        for z in filter(lambda x: not (x.id == self.safety_zone.id), self.zones.values()):
            z.density = value


class TransitWidthError(ValueError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


@dataclass(frozen=True)
class BLine2D:
    p0: BPoint
    p1: BPoint

    def length(self) -> float:
        return math.sqrt(math.pow(self.p0.x - self.p1.x, 2) + math.pow(self.p0.y - self.p1.y, 2))

    @staticmethod
    def new() -> "BLine2D":
        return BLine2D(BPoint(0, 0), BPoint(0, 0))  # pyright: ignore [reportGeneralTypeIssues]

    @staticmethod
    def from_simple_points(p0: Tuple[float, float], p1: Tuple[float, float]) -> "BLine2D":
        return BLine2D(BPoint.from_simple_point(p0), BPoint.from_simple_point(p1))


@dataclass(frozen=True)
class TransitEdges:
    parallel: Tuple[BLine2D, BLine2D]
    normal: Tuple[BLine2D, BLine2D]


class Transit(BBuildElement):
    MIN_WIDTH = 0.5

    def __init__(self, build_element: BBuildElement) -> None:
        super().__init__(
            build_element.id,
            build_element.sign,
            build_element.output,
            build_element.points,
            build_element.name,
            build_element.sizeZ,
        )

        self.potential = 0.0
        self.num_of_people = 0.0
        self.is_visited = False
        self.is_blocked = False
        self.is_safe = True

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, w: float) -> None:
        if w <= self.MIN_WIDTH:
            raise TransitWidthError(f"Width of transit below or equal {self.MIN_WIDTH} is not possible")
        self._width = w

    def calculate_width(self, zone_element1: BBuildElement, zone_element2: Union[BBuildElement, None]) -> bool:
        tr_edges: Union[TransitEdges, None] = self.prepare_transit(zone_element1)
        if tr_edges is not None:
            if self.sign is BSign.DoorWay:
                if zone_element2 is not None:
                    self._width = self._door_way_width(zone_element1, zone_element2)
                else:
                    return False
            else:
                self._width = round((tr_edges.parallel[0].length() + tr_edges.parallel[1].length()) / 2, NDIGITS)
            return True
        return False

    def prepare_transit(self, zone_element: BBuildElement) -> Union[TransitEdges, None]:
        """Сортировка ребер проема на параллельные и перпендикулярные стенам комнат

        ```
        ┌─────────┐ ┌──────────┐
        │         │ │          │
        │      A┌─┼─┼─┐B       │
        │       │ │ │ │        │
        │       │ │ │ │        │
        │      D└─┼─┼─┘C       │
        │         │ │          │
        └─────────┘ └──────────┘
        ```

        AD, BC - parallel
        AB, CD - normal

        Параллельные ребера для вычсиления ширины двери

        Перепендикулярные ребра используются для вычисления ширины виртуального проема
        """

        def _repack_points(points: List[BPoint]) -> List[Point2D]:
            return list(map(lambda p: (p.x, p.y), points[:-1]))

        transit_points = _repack_points(self.points)
        zone_points = _repack_points(zone_element.points)
        zone_tri: Triangles = tripy.earclip(zone_points)

        edge_points = [i for i, p in enumerate(transit_points) if self._point_in_polygon(p, zone_tri)]
        edge_points.sort(reverse=True)

        if not (len(edge_points) == 2):
            return None

        p1 = transit_points.pop(edge_points[0])
        p2 = transit_points.pop(edge_points[1])
        p3 = transit_points.pop(1)
        p4 = transit_points.pop(0)

        parallel = (BLine2D.from_simple_points(p1, p2), BLine2D.from_simple_points(p3, p4))
        normal = (BLine2D.from_simple_points(p1, p3), BLine2D.from_simple_points(p2, p4))

        if normal[0].length() > BLine2D.from_simple_points(p1, p4).length():
            normal = (BLine2D.from_simple_points(p1, p4), BLine2D.from_simple_points(p2, p3))

        te = TransitEdges(parallel, normal)
        return te

    def _point_in_polygon(self, point: Point2D, zone_tri: Triangles) -> bool:
        """
        Проверка вхождения точки в прямоугольник

        Для этого произвоится треангуляция прямоугольника. В данном случае треангуляция осуществляется вручную,
        потому что нам известно, что каждое помещение представляет прямоугольником.
        После получения треугольников поподает ли точка в треугольник, для чего выполняется проверка
        с какой стороны от стороны треугольника находится точка.
        """

        def where_point(a: Point2D, b: Point2D, p: Point2D) -> int:
            """
            Проверка с какой стороны находится точка \n
            a, b, p - точки, представленные массивом [x, y] \n
            ab - вектор \n
            p - точка
            """
            s = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
            if s > 0:
                return 1  # Точка слева от вектора AB
            elif s < 0:
                return -1  # Точка справа от вектора AB
            else:
                return 0  # Точка на векторе, прямо по вектору или сзади вектора

        def is_point_in_triangle(triangle: Triangle, p: Point2D) -> bool:
            """
            Проверка попадания точки в треугольник \n
            triangle - треугольник, представленный массивом [[x, y], [x, y], [x, y]] \n
            p - точка, представленная массивом [x, y] \n
            """
            q1 = where_point(triangle[0], triangle[1], p)
            q2 = where_point(triangle[1], triangle[2], p)
            q3 = where_point(triangle[2], triangle[0], p)
            return q1 >= 0 and q2 >= 0 and q3 >= 0

        """
        Проверяем в какие треугольники попадает точка
        """
        for tr in zone_tri:
            if is_point_in_triangle((tr[0], tr[1], tr[2]), point):
                break
        else:  # В это условие попадаем, если прошли цикл
            return False

        return True

    def _door_way_width(self, zone_element1: BBuildElement, zone_element2: BBuildElement) -> float:
        """
        Возможные варианты стыковки помещений, которые соединены проемом
        Код ниже определяет область их пересечения
        ```
           +----+  +----+     +----+
                |  |               | +----+
                |  |               | |
                |  |               | |
           +----+  +----+          | |
                                   | +----+
           +----+             +----+
                |  +----+
                |  |          +----+ +----+
                |  |               | |
           +----+  |               | |
                   +----+          | +----+
                              +----+
        ```
        *************************************************************************
        1. Определить грани помещения, которые пересекает короткая сторона проема
        2. Вычислить среднее проекций граней друг на друга
        """
        tr_edges: Union[TransitEdges, None] = self.prepare_transit(zone_element1)
        if tr_edges is None:
            return False

        # https://e-maxx.ru/algo/segments_intersection_checking
        def area_of_triangle(p1: BPoint, p2: BPoint, p3: BPoint) -> float:
            """signed area of a triangle"""
            return (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x)

        def intersect_1(p0_a: float, p0_b: float, p1_a: float, p1_b: float) -> bool:
            p0_a, p0_b = (p0_b, p0_a) if (p0_a > p0_b) else (p0_a, p0_b)
            p1_a, p1_b = (p1_b, p1_a) if (p1_a > p1_b) else (p1_a, p1_b)
            return max(p0_a, p1_a) <= min(p0_b, p1_b)

        def is_intersect_line(l1: BLine2D, l2: BLine2D) -> bool:
            """check if two segments intersect"""
            return (
                intersect_1(l1.p0.x, l1.p1.x, l2.p0.x, l2.p1.x)
                and intersect_1(l1.p0.y, l1.p1.y, l2.p0.y, l2.p1.y)
                and area_of_triangle(l1.p0, l1.p1, l2.p0) * area_of_triangle(l1.p0, l1.p1, l2.p1) <= 0
                and area_of_triangle(l2.p0, l2.p1, l1.p0) * area_of_triangle(l2.p0, l2.p1, l1.p1) <= 0
            )

        def intersected_edge(
            polygon: List[BPoint], tline: BLine2D
        ) -> BLine2D:  # pyright: ignore [reportUnusedFunction]
            """ """
            lines: List[Union[BLine2D, None]] = list(
                filter(
                    lambda edge: edge is not None,
                    map(
                        lambda p: BLine2D(p[0], p[1]) if is_intersect_line(tline, BLine2D(p[0], p[1])) else None,
                        zip(polygon, polygon[1:] + polygon[:1]),
                    ),
                )
            )

            if len(lines) > 1 or lines[0] is None:
                raise ValueError("Ошибка геометрии. Проверьте правильность ввода дверей и вирутальных проемов.")

            return lines[0]

        # Определение точки на линии, расстояние до которой от заданной точки является минимальным из существующих
        def nearest_point(point_start: BPoint, line: BLine2D) -> BPoint:  # pyright: ignore [reportUnusedFunction]
            a: BPoint = line.p0  # pyright: ignore [reportGeneralTypeIssues]
            b: BPoint = line.p1  # pyright: ignore [reportGeneralTypeIssues]

            if line.length() < self.MIN_WIDTH:
                raise ValueError("Линия короткая")

            A = point_start.x - a.x
            B = point_start.y - a.y
            C = b.x - a.x
            D = b.y - a.y

            dot = A * C + B * D
            len_sq = C * C + D * D
            param = -1

            if len_sq != 0:
                param = dot / len_sq

            xx: float = 0
            yy: float = 0

            if param < 0:
                xx = a.x
                yy = a.y
            elif param > 1:
                xx = b.x
                yy = b.y
            else:
                xx = a.x + param * C
                yy = a.y + param * D

            return BPoint(xx, yy)  # pyright: ignore [reportGeneralTypeIssues]

        zone_edge1 = intersected_edge(zone_element1.points, tr_edges.normal[0])
        zone_edge2 = intersected_edge(zone_element2.points, tr_edges.normal[1])

        projection_line_1to2 = BLine2D(
            nearest_point(zone_edge1.p0, zone_edge2), nearest_point(zone_edge1.p1, zone_edge2)
        )
        projection_line_2to1 = BLine2D(
            nearest_point(zone_edge2.p0, zone_edge1), nearest_point(zone_edge2.p1, zone_edge1)
        )

        return (projection_line_1to2.length() + projection_line_2to1.length()) / 2

    def __repr__(self) -> str:
        return f"Transit(name:{self.name})"


class Zone(BBuildElement):
    def __init__(self, build_element: BBuildElement) -> None:
        super().__init__(
            build_element.id,
            build_element.sign,
            build_element.output,
            build_element.points,
            build_element.name,
            build_element.sizeZ,
        )

        self._calculate_area()

        self.potential = 0.0
        self.num_of_people = 0.0
        self.is_visited = False
        self.is_blocked = False
        self.is_safe = True
        self.graph_level = 0
        self.density = self.num_of_people / self.area

    @property
    def area(self) -> float:
        return self._area

    def _calculate_area(self):
        def triangle_area(p1: Point2D, p2: Point2D, p3: Point2D) -> float:
            return abs(0.5 * ((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])))

        self._tri: Triangles = tripy.earclip([(p.x, p.y) for p in self.points[:-1]])
        self._area = round(sum(triangle_area(tr[0], tr[1], tr[2]) for tr in self._tri), NDIGITS)

    @property
    def num_of_people(self) -> float:
        return self._num_of_people

    @num_of_people.setter
    def num_of_people(self, n: float) -> None:
        if n < 0:
            raise ValueError("Number of people in zone below 0 is not possible")
        self._num_of_people = n
        self._density = self._num_of_people / self.area

    @property
    def density(self) -> float:
        return self._density

    @density.setter
    def density(self, value: float) -> None:
        if value < 0:
            raise ValueError("Density of people flow in zone below 0 is not possible")
        self._density = value
        self._num_of_people = self._density * self.area

    def __repr__(self) -> str:
        return f"Zone(name:{self.name})"

    def __hash__(self):
        return hash(self.id)


# Tests
if __name__ == "__main__":
    building = mapping_building("resources/building_example.json")
    # Test Zone
    print("Zone test")
    be1 = building.levels[0].elements[1]
    z1 = Zone(be1)
    print(z1.area)

    # for l in building.levels:
    #     for e in l.elements:
    #         z1 = Zone(e)
    #         print(z1.get_area())

    # Test Transit
    print("Transit test")
    # z1: Zone
    be1 = list(filter(lambda be: be.id == UUID("4199e3d7-5f08-4aab-8997-3b7cb1cd8cd8"), building.levels[0].elements))[0]
    t1: Transit = Transit(
        list(filter(lambda be: be.id == UUID("f46361f4-a99f-4e79-aebe-d36ebed45992"), building.levels[0].elements))[0]
    )

    print(z1)
    print(t1)
    # FIXME: add second zone
    # t1.calculate_width(be1)
    print(t1.width)

    # Test Bim
    print("== BIM test ==")
    bim = Bim(building)
    v: Transit
    for k, v in bim.transits.items():
        print(k, v.width)

    print(bim.safety_zone.area)

    # triangulation example
    import numpy as np
    import matplotlib.pyplot as plt

    points = [
        (35.97872543334961, -34.659114837646484),
        (35.97872543334961, -37.01911163330078),
        (33.9708251953125, -37.01911163330078),
        (33.9708251953125, -37.219112396240234),
        (34.07872772216797, -37.219112396240234),
        (34.0787277221679, -38.4352912902832),
        (33.15372467041016, -38.4352912902832),
        (33.153724670410156, -37.219112396240234),
        (33.25210189819336, -37.219112396240234),
        (33.25210189819336, -37.01911163330078),
        (32.90689468383789, -37.01911163330078),
        (32.90689468383789, -37.219112396240234),
        (33.003726959228516, -37.219112396240234),
        (33.00372695922856, -38.4352912902832),
        (32.0787277221679, -38.4352912902832),
        (32.07872772216797, -37.219112396240234),
        (32.193763732910156, -37.219112396240234),
        (32.19376373291015, -37.01911163330078),
        (30.50872802734375, -37.01911163330078),
        (30.50872802734375, -34.659114837646484),
        (35.97872543334961, -34.659114837646484),
    ]

    plot_points = np.array([[point[0], point[1]] for point in points])

    triangles = tripy.earclip(points)

    tri = np.array([[list(triangle[0]), list(triangle[1]), list(triangle[2])] for triangle in triangles])

    print(tri)

    for triangle in tri:
        plt.plot(triangle[:, 0], triangle[:, 1], "go-")  # pyright: ignore [reportUnknownMemberType]

    plt.plot(plot_points[:, 0], plot_points[:, 1], "o")  # pyright: ignore [reportUnknownMemberType]
    plt.show()  # pyright: ignore [reportUnknownMemberType]
