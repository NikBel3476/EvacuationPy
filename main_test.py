from matplotlib.testing.decorators import image_comparison  # pyright: ignore [reportUnknownVariableType]
import matplotlib.pyplot as plt
import BimDataModel
from BimTools import Bim
from BimComplexity import BimComplexity
from BimEvac import Moving
from typing import List


class TestModelingExamples:
    @image_comparison(baseline_images=["example_one_exit"], extensions=["png"], style="mpl20")
    def test_example_one_exit(self):
        building = BimDataModel.mapping_building("resources/example-one-exit.json")

        bim = Bim(building)
        BimComplexity(bim)  # check a building

        wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

        # Doors width
        for t in bim.transits.values():
            t.width = 2.0

        density_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # м2/м2
        timestamps_list = [15.0, 20.0, 25.5, 30.0, 36.4, 42.9, 52.2, 63.2, 80.0]  # сек.

        times: List[float] = []  # сек.
        for density in density_list:
            m = Moving()
            bim.set_density(m.pfv.to_pm2(density))

            num_of_people = 0.0
            for z in wo_safety:
                num_of_people += z.num_of_people

            nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
            time = 0.0  # сек.
            while nop >= 10e-3:
                m.step(bim)
                time += Moving.MODELLING_STEP
                nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
                if nop <= 0:
                    break

            times.append(round(time * 60, 1))

        p: List[float] = []
        for i in range(len(timestamps_list)):
            p.append(round(timestamps_list[i] / times[i], 2))

        _, ax = plt.subplots()  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
        ax.plot(  # pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
            density_list, times, linewidth=2.0, c="darkorange"
        )

    @image_comparison(baseline_images=["example_two_exits"], extensions=["png"], style="mpl20")
    def test_example_two_exits(self):
        building = BimDataModel.mapping_building("resources/example-two-exits.json")

        bim = Bim(building)
        BimComplexity(bim)  # check a building

        wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

        # Doors width
        for t in bim.transits.values():
            t.width = 2.0

        density_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # м2/м2
        timestamp_list = [15.0, 20.0, 25.5, 30.0, 36.4, 42.9, 52.2, 63.2, 80.0]  # сек.

        times: List[float] = []  # сек.
        for density in density_list:
            m = Moving()
            bim.set_density(m.pfv.to_pm2(density))

            num_of_people = 0.0
            for z in wo_safety:
                num_of_people += z.num_of_people

            nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
            time = 0.0
            while nop >= 10e-3:
                m.step(bim)
                time += Moving.MODELLING_STEP
                nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
                if nop <= 0:
                    break

            times.append(round(time * 60, 1))

        p: List[float] = []
        for i in range(len(timestamp_list)):
            p.append(round(timestamp_list[i] / times[i], 2))

        _, ax = plt.subplots()  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
        ax.plot(  # pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
            density_list, times, linewidth=2.0, c="darkorange"
        )

    @image_comparison(baseline_images=["building_example"], extensions=["png"], style="mpl20")
    def test_building_example(self):
        building = BimDataModel.mapping_building("resources/building_example.json")

        bim = Bim(building)
        BimComplexity(bim)  # check a building

        wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

        # Doors width
        for t in bim.transits.values():
            t.width = 2.0

        density_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # м2/м2
        timestamp_list = [15.0, 20.0, 25.5, 30.0, 36.4, 42.9, 52.2, 63.2, 80.0]  # сек.

        times: List[float] = []  # сек.

        for density in density_list:
            m = Moving()
            bim.set_density(m.pfv.to_pm2(density))

            num_of_people = 0.0
            for z in wo_safety:
                num_of_people += z.num_of_people

            nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
            time = 0.0
            while nop >= 10e-3:
                m.step(bim)
                time += Moving.MODELLING_STEP
                nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
                if nop <= 0:
                    break

            times.append(round(time * 60, 1))

        p: List[float] = []
        for i in range(len(timestamp_list)):
            p.append(round(timestamp_list[i] / times[i], 2))

        _, ax = plt.subplots()  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
        ax.plot(  # pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
            density_list, times, linewidth=2.0, c="darkorange"
        )

    @image_comparison(baseline_images=["one_zone_one_exit"], extensions=["png"], style="mpl20")
    def test_one_zone_one_exit(self):
        building = BimDataModel.mapping_building("resources/one_zone_one_exit.json")

        bim = Bim(building)
        BimComplexity(bim)  # check a building

        wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

        # Doors width
        for t in bim.transits.values():
            t.width = 2.0

        density_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # м2/м2
        timestamp_list = [15.0, 20.0, 25.5, 30.0, 36.4, 42.9, 52.2, 63.2, 80.0]  # сек.

        times: List[float] = []  # сек.

        for density in density_list:
            m = Moving()
            bim.set_density(m.pfv.to_pm2(density))

            num_of_people = 0.0
            for z in wo_safety:
                num_of_people += z.num_of_people

            nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
            time = 0.0
            while nop >= 10e-3:
                m.step(bim)
                time += Moving.MODELLING_STEP
                nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
                if nop <= 0:
                    break

            times.append(round(time * 60, 1))

        p: List[float] = []
        for i in range(len(timestamp_list)):
            p.append(round(timestamp_list[i] / times[i], 2))

        _, ax = plt.subplots()  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
        ax.plot(  # pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
            density_list, times, linewidth=2.0, c="darkorange"
        )

    @image_comparison(baseline_images=["three_zones_three_transits"], extensions=["png"], style="mpl20")
    def test_three_zones_three_transits(self):
        building = BimDataModel.mapping_building("resources/three_zones_three_transits.json")

        bim = Bim(building)
        BimComplexity(bim)  # check a building

        wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

        # Doors width
        for t in bim.transits.values():
            t.width = 2.0

        density_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # м2/м2
        timestamp_list = [15.0, 20.0, 25.5, 30.0, 36.4, 42.9, 52.2, 63.2, 80.0]  # сек.

        times: List[float] = []  # сек.

        for density in density_list:
            m = Moving()
            bim.set_density(m.pfv.to_pm2(density))

            num_of_people = 0.0
            for z in wo_safety:
                num_of_people += z.num_of_people

            nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
            time = 0.0
            while nop >= 10e-3:
                m.step(bim)
                time += Moving.MODELLING_STEP
                nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
                if nop <= 0:
                    break

            times.append(round(time * 60, 1))

        p: List[float] = []
        for i in range(len(timestamp_list)):
            p.append(round(timestamp_list[i] / times[i], 2))

        _, ax = plt.subplots()  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
        ax.plot(  # pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
            density_list, times, linewidth=2.0, c="darkorange"
        )

    @image_comparison(baseline_images=["two_levels"], extensions=["png"], style="mpl20")
    def test_two_levels(self):
        building = BimDataModel.mapping_building("resources/two_levels.json")

        bim = Bim(building)
        BimComplexity(bim)  # check a building

        wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

        # Doors width
        for t in bim.transits.values():
            t.width = 2.0

        density_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # м2/м2
        timestamp_list = [15.0, 20.0, 25.5, 30.0, 36.4, 42.9, 52.2, 63.2, 80.0]  # сек.

        times: List[float] = []  # сек.

        for density in density_list:
            m = Moving()
            bim.set_density(m.pfv.to_pm2(density))

            num_of_people = 0.0
            for z in wo_safety:
                num_of_people += z.num_of_people

            nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
            time = 0.0
            while nop >= 10e-3:
                m.step(bim)
                time += Moving.MODELLING_STEP
                nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
                if nop <= 0:
                    break

            times.append(round(time * 60, 1))

        p: List[float] = []
        for i in range(len(timestamp_list)):
            p.append(round(timestamp_list[i] / times[i], 2))

        _, ax = plt.subplots()  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
        ax.plot(  # pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
            density_list, times, linewidth=2.0, c="darkorange"
        )

    @image_comparison(baseline_images=["udsu_block_1"], extensions=["png"], style="mpl20")
    def test_udsu_block_1(self):
        building = BimDataModel.mapping_building("resources/udsu_block_1.json")

        bim = Bim(building)
        BimComplexity(bim)  # check a building

        wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

        # Doors width
        for t in bim.transits.values():
            t.width = 2.0

        density_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # м2/м2
        timestamp_list = [15.0, 20.0, 25.5, 30.0, 36.4, 42.9, 52.2, 63.2, 80.0]  # сек.

        times: List[float] = []  # сек.

        for density in density_list:
            m = Moving()
            bim.set_density(m.pfv.to_pm2(density))

            num_of_people = 0.0
            for z in wo_safety:
                num_of_people += z.num_of_people

            nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
            time = 0.0
            while nop >= 10e-3:
                m.step(bim)
                time += Moving.MODELLING_STEP
                nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
                if nop <= 0:
                    break

            times.append(round(time * 60, 1))

        p: List[float] = []
        for i in range(len(timestamp_list)):
            p.append(round(timestamp_list[i] / times[i], 2))

        _, ax = plt.subplots()  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
        ax.plot(  # pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
            density_list, times, linewidth=2.0, c="darkorange"
        )

    @image_comparison(baseline_images=["udsu_block_2"], extensions=["png"], style="mpl20")
    def test_udsu_block_2(self):
        building = BimDataModel.mapping_building("resources/udsu_block_2.json")

        bim = Bim(building)
        BimComplexity(bim)  # check a building

        wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

        # Doors width
        for t in bim.transits.values():
            t.width = 2.0

        density_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # м2/м2
        timestamp_list = [15.0, 20.0, 25.5, 30.0, 36.4, 42.9, 52.2, 63.2, 80.0]  # сек.

        times: List[float] = []  # сек.

        for density in density_list:
            m = Moving()
            bim.set_density(m.pfv.to_pm2(density))

            num_of_people = 0.0
            for z in wo_safety:
                num_of_people += z.num_of_people

            nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
            time = 0.0
            while nop >= 10e-3:
                m.step(bim)
                time += Moving.MODELLING_STEP
                nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
                if nop <= 0:
                    break

            times.append(round(time * 60, 1))

        p: List[float] = []
        for i in range(len(timestamp_list)):
            p.append(round(timestamp_list[i] / times[i], 2))

        _, ax = plt.subplots()  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
        ax.plot(  # pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
            density_list, times, linewidth=2.0, c="darkorange"
        )

    @image_comparison(baseline_images=["udsu_block_3"], extensions=["png"], style="mpl20")
    def test_udsu_block_3(self):
        building = BimDataModel.mapping_building("resources/udsu_block_3.json")

        bim = Bim(building)
        BimComplexity(bim)  # check a building

        wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

        # Doors width
        for t in bim.transits.values():
            t.width = 2.0

        density_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # м2/м2
        timestamp_list = [15.0, 20.0, 25.5, 30.0, 36.4, 42.9, 52.2, 63.2, 80.0]  # сек.

        times: List[float] = []  # сек.

        for density in density_list:
            m = Moving()
            bim.set_density(m.pfv.to_pm2(density))

            num_of_people = 0.0
            for z in wo_safety:
                num_of_people += z.num_of_people

            nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
            time = 0.0
            while nop >= 10e-3:
                m.step(bim)
                time += Moving.MODELLING_STEP
                nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
                if nop <= 0:
                    break

            times.append(round(time * 60, 1))

        p: List[float] = []
        for i in range(len(timestamp_list)):
            p.append(round(timestamp_list[i] / times[i], 2))

        _, ax = plt.subplots()  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
        ax.plot(  # pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
            density_list, times, linewidth=2.0, c="darkorange"
        )

    @image_comparison(baseline_images=["udsu_block_4"], extensions=["png"], style="mpl20")
    def test_udsu_block_4(self):
        building = BimDataModel.mapping_building("resources/udsu_block_4.json")

        bim = Bim(building)
        BimComplexity(bim)  # check a building

        wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

        # Doors width
        for t in bim.transits.values():
            t.width = 2.0

        density_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # м2/м2
        timestamp_list = [15.0, 20.0, 25.5, 30.0, 36.4, 42.9, 52.2, 63.2, 80.0]  # сек.

        times: List[float] = []  # сек.

        for density in density_list:
            m = Moving()
            bim.set_density(m.pfv.to_pm2(density))

            num_of_people = 0.0
            for z in wo_safety:
                num_of_people += z.num_of_people

            nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
            time = 0.0
            while nop >= 10e-3:
                m.step(bim)
                time += Moving.MODELLING_STEP
                nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
                if nop <= 0:
                    break

            times.append(round(time * 60, 1))

        p: List[float] = []
        for i in range(len(timestamp_list)):
            p.append(round(timestamp_list[i] / times[i], 2))

        _, ax = plt.subplots()  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
        ax.plot(  # pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
            density_list, times, linewidth=2.0, c="darkorange"
        )

    @image_comparison(baseline_images=["udsu_block_5"], extensions=["png"], style="mpl20")
    def test_udsu_block_5(self):
        building = BimDataModel.mapping_building("resources/udsu_block_5.json")

        bim = Bim(building)
        BimComplexity(bim)  # check a building

        wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

        # Doors width
        for t in bim.transits.values():
            t.width = 2.0

        density_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # м2/м2
        timestamp_list = [15.0, 20.0, 25.5, 30.0, 36.4, 42.9, 52.2, 63.2, 80.0]  # сек.

        times: List[float] = []  # сек.

        for density in density_list:
            m = Moving()
            bim.set_density(m.pfv.to_pm2(density))

            num_of_people = 0.0
            for z in wo_safety:
                num_of_people += z.num_of_people

            nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
            time = 0.0
            while nop >= 10e-3:
                m.step(bim)
                time += Moving.MODELLING_STEP
                nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
                if nop <= 0:
                    break

            times.append(round(time * 60, 1))

        p: List[float] = []
        for i in range(len(timestamp_list)):
            p.append(round(timestamp_list[i] / times[i], 2))

        _, ax = plt.subplots()  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
        ax.plot(  # pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
            density_list, times, linewidth=2.0, c="darkorange"
        )

    @image_comparison(baseline_images=["udsu_block_7"], extensions=["png"], style="mpl20")
    def test_udsu_block_7(self):
        building = BimDataModel.mapping_building("resources/udsu_block_7.json")

        bim = Bim(building)
        BimComplexity(bim)  # check a building

        wo_safety = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

        # Doors width
        for t in bim.transits.values():
            t.width = 2.0

        density_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # м2/м2
        timestamp_list = [15.0, 20.0, 25.5, 30.0, 36.4, 42.9, 52.2, 63.2, 80.0]  # сек.

        times: List[float] = []  # сек.

        for density in density_list:
            m = Moving()
            bim.set_density(m.pfv.to_pm2(density))

            num_of_people = 0.0
            for z in wo_safety:
                num_of_people += z.num_of_people

            nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
            time = 0.0
            while nop >= 10e-3:
                m.step(bim)
                time += Moving.MODELLING_STEP
                nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
                if nop <= 0:
                    break

            times.append(round(time * 60, 1))

        p: List[float] = []
        for i in range(len(timestamp_list)):
            p.append(round(timestamp_list[i] / times[i], 2))

        _, ax = plt.subplots()  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
        ax.plot(  # pyright: ignore [reportUnknownMemberType, reportGeneralTypeIssues]
            density_list, times, linewidth=2.0, c="darkorange"
        )
