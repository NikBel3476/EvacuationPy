from uuid import UUID
import math
import pytest
import tripy
from BimDataModel import BBuildElement, BPoint, BSign
from BimTools import Zone, BLine2D, Transit
from typing import Tuple


class TestBimToolsBLine2D:
    def test_length(self):
        line = BLine2D(BPoint(-1.0, -1.0), BPoint(1.0, 1.0))  # pyright: ignore [reportGeneralTypeIssues]
        assert line.length() == math.sqrt(8)


class TestBimToolsTransit:
    @pytest.mark.parametrize(
        "point", [(0.0, 0.0), (0.5, 0.0), (1.0, 0.0), (0.5, 0.5), (0.0, 1.0), (0.0, 0.5), (0.0, 0.0)]
    )
    def test_point_inside_triangle(self, point: Tuple[float, float]):
        build_element = BBuildElement(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            sign=BSign.DoorWay,
            output=[],
            points=[],
            name="transit",
            sizeZ=3.0,
        )

        polygon = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]

        tri = tripy.earclip(polygon)
        transit = Transit(build_element)

        assert transit._point_in_polygon(point, tri)  # pyright: ignore [reportPrivateUsage]

    @pytest.mark.parametrize("point", [(-1.0, -1.0), (0.5, -1.0), (1.5, -0.5), (1.0, 1.0), (-0.5, 1.5), (-0.5, 0.5)])
    def test_point_outside_triangle(self, point: Tuple[float, float]):
        build_element = BBuildElement(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            sign=BSign.DoorWay,
            output=[],
            points=[],
            name="transit",
            sizeZ=3.0,
        )

        polygon = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]

        tri = tripy.earclip(polygon)
        transit = Transit(build_element)

        assert not transit._point_in_polygon(point, tri)  # pyright: ignore [reportPrivateUsage]

    @pytest.mark.parametrize(
        "point",
        [
            (0.0, 0.0),
            (0.5, 0.0),
            (1.0, 0.0),
            (1.0, 0.5),
            (1.0, 1.0),
            (0.5, 1.0),
            (0.0, 1.0),
            (0.0, 0.5),
            (0.5, 0.5),
        ],
    )
    def test_point_inside_square(self, point: Tuple[float, float]):
        build_element = BBuildElement(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            sign=BSign.DoorWay,
            output=[],
            points=[],
            name="transit",
            sizeZ=3.0,
        )

        polygon = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

        tri = tripy.earclip(polygon)
        transit = Transit(build_element)

        assert transit._point_in_polygon(point, tri)  # pyright: ignore [reportPrivateUsage]

    @pytest.mark.parametrize(
        "point", [(-0.5, -0.5), (0.5, -0.5), (1.5, -0.5), (1.5, 0.5), (1.5, 1.5), (0.5, 1.5), (-0.5, 1.5), (-0.5, 0.5)]
    )
    def test_point_outside_square(self, point: Tuple[float, float]):
        build_element = BBuildElement(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            sign=BSign.DoorWay,
            output=[],
            points=[],
            name="transit",
            sizeZ=3.0,
        )

        polygon = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]

        tri = tripy.earclip(polygon)
        transit = Transit(build_element)

        assert not transit._point_in_polygon(point, tri)  # pyright: ignore [reportPrivateUsage]

    def test_rectangles_intersection(self):
        build_element = BBuildElement(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            sign=BSign.DoorWay,
            output=[],
            points=[],
            name="transit",
            sizeZ=3.0,
        )

        polygon = [
            [
                1.0804720876503242,
                9.784116583159095,
            ],
            [
                9.452596550210751,
                9.830117267019318,
            ],
            [
                9.475596892140864,
                1.2969904109481103,
            ],
            [
                1.1034724295804352,
                1.2969904109481103,
            ],
        ]

        points_outside = [
            (
                7.198563041059868,
                10.888132995804426,
            ),
            (
                8.877588001957976,
                10.934133679664647,
            ),
        ]

        points_inside = [
            (
                8.854587660027866,
                9.577113505788097,
            ),
            (
                7.198563041059868,
                9.554113163857984,
            ),
        ]

        tri = tripy.earclip(polygon)
        transit = Transit(build_element)

        assert (
            transit._point_in_polygon(points_inside[0], tri)  # pyright: ignore [reportPrivateUsage]
            and transit._point_in_polygon(points_inside[1], tri)  # pyright: ignore [reportPrivateUsage]
            and not transit._point_in_polygon(points_outside[0], tri)  # pyright: ignore [reportPrivateUsage]
            and not transit._point_in_polygon(points_outside[1], tri)  # pyright: ignore [reportPrivateUsage]
        )

    def test_intersection_of_a_figure_and_a_rectangle(self):
        build_element = BBuildElement(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            sign=BSign.DoorWay,
            output=[],
            points=[],
            name="transit",
            sizeZ=3.0,
        )

        polygon = [
            [
                35.97872543334961,
                -34.659114837646484,
            ],
            [
                35.97872543334961,
                -37.01911163330078,
            ],
            [
                33.9708251953125,
                -37.01911163330078,
            ],
            [
                33.9708251953125,
                -37.219112396240234,
            ],
            [
                34.07872772216797,
                -37.219112396240234,
            ],
            [
                34.0787277221679,
                -38.4352912902832,
            ],
            [
                33.15372467041016,
                -38.4352912902832,
            ],
            [
                33.153724670410156,
                -37.219112396240234,
            ],
            [
                33.25210189819336,
                -37.219112396240234,
            ],
            [
                33.25210189819336,
                -37.01911163330078,
            ],
            [
                32.90689468383789,
                -37.01911163330078,
            ],
            [
                32.90689468383789,
                -37.219112396240234,
            ],
            [
                33.003726959228516,
                -37.219112396240234,
            ],
            [
                33.00372695922856,
                -38.4352912902832,
            ],
            [
                32.0787277221679,
                -38.4352912902832,
            ],
            [
                32.07872772216797,
                -37.219112396240234,
            ],
            [
                32.193763732910156,
                -37.219112396240234,
            ],
            [
                32.19376373291015,
                -37.01911163330078,
            ],
            [
                30.50872802734375,
                -37.01911163330078,
            ],
            [
                30.50872802734375,
                -34.659114837646484,
            ],
        ]

        points_outside = [
            (
                31.87872886657715,
                -38.24702072143555,
            ),
            (
                31.87872886657715,
                -37.34701919555664,
            ),
        ]

        points_inside = [
            (
                32.07872772216797,
                -38.24702072143555,
            ),
            (
                32.07872772216797,
                -37.34701919555664,
            ),
        ]

        tri = tripy.earclip(polygon)
        transit = Transit(build_element)

        assert (
            transit._point_in_polygon(points_inside[0], tri)  # pyright: ignore [reportPrivateUsage]
            and transit._point_in_polygon(points_inside[1], tri)  # pyright: ignore [reportPrivateUsage]
            and not transit._point_in_polygon(points_outside[0], tri)  # pyright: ignore [reportPrivateUsage]
            and not transit._point_in_polygon(points_outside[1], tri)  # pyright: ignore [reportPrivateUsage]
        )


class TestBimToolsZone:
    def test_area_calculation_triangle(self):
        build_element = BBuildElement(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            sign=BSign.Room,
            output=[UUID("00000000-0000-0000-0000-000000000001"), UUID("00000000-0000-0000-0000-000000000002")],
            points=[
                BPoint(x=0.0, y=-1.0),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=1.0, y=0.0),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=0.0, y=1.0),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=0.0, y=-1.0),  # pyright: ignore [reportGeneralTypeIssues]
            ],
            name="room for area test",
            sizeZ=3.0,
        )

        zone_triangle = Zone(build_element)

        assert zone_triangle.area == 1.0

    def test_area_calculation_parallelogram(self):
        build_element = BBuildElement(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            sign=BSign.Room,
            output=[UUID("00000000-0000-0000-0000-000000000001"), UUID("00000000-0000-0000-0000-000000000002")],
            points=[
                BPoint(x=-2.0, y=-1.0),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=2.0, y=-1.0),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=3.0, y=1.0),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=-1.0, y=1.0),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=-2.0, y=-1.0),  # pyright: ignore [reportGeneralTypeIssues]
            ],
            name="room for area test",
            sizeZ=3.0,
        )

        zone_triangle = Zone(build_element)

        assert zone_triangle.area == 8.0

    def test_area_calculation_complex_figure_with_right_angles(self):
        build_element = BBuildElement(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            sign=BSign.Room,
            output=[UUID("00000000-0000-0000-0000-000000000001"), UUID("00000000-0000-0000-0000-000000000002")],
            points=[
                BPoint(x=35.97872543334961, y=-34.659114837646484),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=35.97872543334961, y=-37.01911163330078),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=33.9708251953125, y=-37.01911163330078),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=33.9708251953125, y=-37.219112396240234),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=34.07872772216797, y=-37.219112396240234),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=34.0787277221679, y=-38.4352912902832),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=33.15372467041016, y=-38.4352912902832),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=33.153724670410156, y=-37.219112396240234),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=33.25210189819336, y=-37.219112396240234),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=33.25210189819336, y=-37.01911163330078),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=32.90689468383789, y=-37.01911163330078),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=32.90689468383789, y=-37.219112396240234),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=33.003726959228516, y=-37.219112396240234),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=33.00372695922856, y=-38.4352912902832),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=32.0787277221679, y=-38.4352912902832),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=32.07872772216797, y=-37.219112396240234),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=32.193763732910156, y=-37.219112396240234),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=32.19376373291015, y=-37.01911163330078),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=30.50872802734375, y=-37.01911163330078),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=30.50872802734375, y=-34.659114837646484),  # pyright: ignore [reportGeneralTypeIssues]
                BPoint(x=35.97872543334961, y=-34.659114837646484),  # pyright: ignore [reportGeneralTypeIssues]
            ],
            name="room for area test",
            sizeZ=3.0,
        )

        zone_triangle = Zone(build_element)

        assert zone_triangle.area == 15.445482030030712
