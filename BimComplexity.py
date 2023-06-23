from BimTools import Bim, Transit, Zone
from typing import List


class BimComplexity(object):
    def __init__(self, bim: Bim) -> None:
        self.bim = bim
        self.number_of_zones = len(self.bim.zones) - 1  # вычитаем безопасную зону
        self.number_of_transits = len(self.bim.transits)
        self.depth_of_bim_graph = 0
        self.width_of_bim_graph = 0
        self._calulate()

    @property
    def number_of_zones(self) -> int:
        return self._number_of_zones

    @number_of_zones.setter
    def number_of_zones(self, val: int) -> None:
        self._number_of_zones = val

    @property
    def number_of_transits(self) -> int:
        return self._number_of_transits

    @number_of_transits.setter
    def number_of_transits(self, val: int) -> None:
        self._number_of_transits = val

    @property
    def width_of_bim_graph(self) -> int:
        return self._width_of_bim_graph

    @width_of_bim_graph.setter
    def width_of_bim_graph(self, val: int) -> None:
        self._width_of_bim_graph = val

    @property
    def depth_of_bim_graph(self) -> int:
        return self._depth_of_bim_graph

    @depth_of_bim_graph.setter
    def depth_of_bim_graph(self, val: int) -> None:
        self._depth_of_bim_graph = val

    def _calulate(self):
        zones_to_process = set([self.bim.safety_zone])
        receiving_zone: Zone = zones_to_process.pop()

        graph_level_elemnts: List[int] = []
        current_graph_level = 0
        max_graph_level = 0

        while True:
            current_graph_level = receiving_zone.graph_level
            max_graph_level = max(max_graph_level, receiving_zone.graph_level)

            transit: Transit
            for transit in (self.bim.transits[tid] for tid in receiving_zone.output):
                if transit.is_visited or transit.is_blocked:
                    continue

                giving_zone: Zone = self.bim.zones[transit.output[0]]
                if giving_zone.id == receiving_zone.id and len(transit.output) > 1:
                    giving_zone = self.bim.zones[transit.output[1]]

                if giving_zone.is_visited:
                    continue

                giving_zone.graph_level = current_graph_level + 1

                if len(graph_level_elemnts) - 1 < giving_zone.graph_level:
                    graph_level_elemnts.append(1)
                else:
                    graph_level_elemnts[giving_zone.graph_level] += 1

                zones_to_process.add(giving_zone)

                giving_zone.is_visited = True
                transit.is_visited = True

            if len(zones_to_process) == 0:
                break

            receiving_zone = zones_to_process.pop()

        self.width_of_bim_graph = max(graph_level_elemnts)
        self.depth_of_bim_graph = max_graph_level

        visited_zones = list(filter(lambda x: x.is_visited, self.bim.zones.values()))
        if len(visited_zones) != len(self.bim.zones.values()) - 1:
            import inspect
            from types import FrameType
            from typing import Union

            frame: Union[FrameType, None] = inspect.currentframe()
            print(
                f">GraphConnectivityException[{__file__}:{frame.f_lineno if frame is not None else ()}]: Connectivity on the graph is broken. Zones below is unreachable:"
            )
            for z in filter(lambda x: not x.is_visited and not (x.name == "Safety zone"), self.bim.zones.values()):
                print(f"{z.sign.name}({z.id}, {z.name}) on level at {z.points[0].z}")

            print(">>QGIS expression for find unreachable zones (use 'Select Features Using Expression'):")
            print(
                " or ".join(
                    f"id is '{z.id}'"
                    for z in filter(
                        lambda x: not x.is_visited and not (x.name == "Safety zone"), self.bim.zones.values()
                    )
                )
            )
            exit()

    def __str__(self) -> str:
        return f"N_w = {self.number_of_zones} - Количество помещений\nN_b = {self.number_of_transits} - Количество дверей\nM_w = {self.width_of_bim_graph} - Ширина графа\nL_w = {self.depth_of_bim_graph} - Глубина графа"
