from uuid import UUID
from BimDataModel import BBuildElement, BPoint, BSign
from BimTools import Zone

class TestBimTools:
    def test_area_calculation_triangle(self):
        build_element = BBuildElement(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            sign=BSign.Room,
            output=[
                UUID("00000000-0000-0000-0000-000000000001"),
                UUID("00000000-0000-0000-0000-000000000002")
            ],
            points=[
                BPoint(x=0.0, y=-1.0),
                BPoint(x=1.0, y=0.0),
                BPoint(x=0.0, y=1.0),
                BPoint(x=0.0, y=-1.0),
            ],
            name="room for area test",
            sizeZ=3.0
        )

        zone_triangle = Zone(build_element)

        assert zone_triangle.area == 1.0

    def test_area_calculation_parallelogram(self):
        build_element = BBuildElement(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            sign=BSign.Room,
            output=[
                UUID("00000000-0000-0000-0000-000000000001"),
                UUID("00000000-0000-0000-0000-000000000002")
            ],
            points=[
                BPoint(x=-2.0, y=-1.0),
                BPoint(x=2.0, y=-1.0),
                BPoint(x=3.0, y=1.0),
                BPoint(x=-1.0, y=1.0),
                BPoint(x=-2.0, y=-1.0),
            ],
            name="room for area test",
            sizeZ=3.0
        )

        zone_triangle = Zone(build_element)

        assert zone_triangle.area == 8.0

    def test_area_calculation_complex_figure_with_right_angles(self):
        build_element = BBuildElement(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            sign=BSign.Room,
            output=[
                UUID("00000000-0000-0000-0000-000000000001"),
                UUID("00000000-0000-0000-0000-000000000002")
            ],
            points=[
                BPoint(
                    x=35.97872543334961,
                    y=-34.659114837646484
                ),
                BPoint(
                    x=35.97872543334961,
                    y=-37.01911163330078
                ),
                BPoint(
                    x=33.9708251953125,
                    y=-37.01911163330078
                ),
                BPoint(
                    x=33.9708251953125,
                    y=-37.219112396240234
                ),
                BPoint(
                    x=34.07872772216797,
                    y=-37.219112396240234
                ),
                BPoint(
                    x=34.0787277221679,
                    y=-38.4352912902832
                ),
                BPoint(
                    x=33.15372467041016,
                    y=-38.4352912902832
                ),
                BPoint(
                    x=33.153724670410156,
                    y=-37.219112396240234
                ),
                BPoint(
                    x=33.25210189819336,
                    y=-37.219112396240234
                ),
                BPoint(
                    x=33.25210189819336,
                    y=-37.01911163330078
                ),
                BPoint(
                    x=32.90689468383789,
                    y=-37.01911163330078
                ),
                BPoint(
                    x=32.90689468383789,
                    y=-37.219112396240234
                ),
                BPoint(
                    x=33.003726959228516,
                    y=-37.219112396240234
                ),
                BPoint(
                    x=33.00372695922856,
                    y=-38.4352912902832
                ),
                BPoint(
                    x=32.0787277221679,
                    y=-38.4352912902832
                ),
                BPoint(
                    x=32.07872772216797,
                    y=-37.219112396240234
                ),
                BPoint(
                    x=32.193763732910156,
                    y=-37.219112396240234
                ),
                BPoint(
                    x=32.19376373291015,
                    y=-37.01911163330078
                ),
                BPoint(
                    x=30.50872802734375,
                    y=-37.01911163330078
                ),
                BPoint(
                    x=30.50872802734375,
                    y=-34.659114837646484
                ),
                BPoint(
                    x=35.97872543334961,
                    y=-34.659114837646484
                ),
            ],
            name="room for area test",
            sizeZ=3.0
        )

        zone_triangle = Zone(build_element)

        assert zone_triangle.area == 15.44548203003071
