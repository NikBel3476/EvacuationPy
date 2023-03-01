from BimTools import Bim, Transit, Zone

class BimComplexity(object):

    def __init__(self, bim:Bim) -> None:
        self.bim = bim
        self.number_of_zones = len(self.bim.zones)-1 #вычитаем безопасную зону
        self.number_of_transits = len(self.bim.transits)
        self.depth_of_bim_graph = 0
        self.width_of_bim_graph = 0
        self._calulate()

    @property
    def number_of_zones(self) -> int:
        return self._number_of_zones
    
    @number_of_zones.setter
    def number_of_zones(self, val:int) -> None:
        self._number_of_zones = val

    @property
    def number_of_transits(self) -> int:
        return self._number_of_transits
    
    @number_of_transits.setter
    def number_of_transits(self, val:int) -> None:
        self._number_of_transits = val

    @property
    def width_of_bim_graph(self) -> int:
        return self._width_of_bim_graph
    
    @width_of_bim_graph.setter
    def width_of_bim_graph(self, val:int) -> None:
        self._width_of_bim_graph = val

    @property
    def depth_of_bim_graph(self) -> int:
        return self._depth_of_bim_graph
    
    @depth_of_bim_graph.setter
    def depth_of_bim_graph(self, val:int) -> None:
        self._depth_of_bim_graph = val

    def _calulate(self):
        zones_to_process = set([self.bim.safety_zone])
        receiving_zone: Zone = zones_to_process.pop()

        graph_level_elemnts = []
        current_graph_level = 0
        max_graph_level = 0

        while True:
            current_graph_level = receiving_zone.graph_level

            transit: Transit
            for transit in (self.bim.transits[tid] for tid in receiving_zone.output):
                if transit.is_visited or transit.is_blocked:
                    continue

                giving_zone: Zone = self.bim.zones[transit.output[0]]
                if giving_zone.id == receiving_zone.id:
                    giving_zone = self.bim.zones[transit.output[1]]
                
                # if giving_zone.graph_level != 0:
                #     print(giving_zone, giving_zone.graph_level)
                giving_zone.graph_level = current_graph_level + 1
                transit.is_visited = True

                if len(graph_level_elemnts) - 1 < giving_zone.graph_level:
                    graph_level_elemnts.append(1)
                else:
                    graph_level_elemnts[giving_zone.graph_level] += 1

                if len(giving_zone.output) > 1: # отсекаем помещения, в которых одна дверь
                    zones_to_process.add(giving_zone)

                max_graph_level = max(max_graph_level, giving_zone.graph_level)
                # print(giving_zone.name, giving_zone.graph_level)

            if len(zones_to_process) == 0:
                break
            
            receiving_zone = zones_to_process.pop()
        
        self.width_of_bim_graph = max(graph_level_elemnts)
        self.depth_of_bim_graph = max_graph_level

    
    def __str__(self) -> str:
        return f"N_w = {self.number_of_zones} - Количество помещений\nN_b = {self.number_of_transits} - Количество дверей\nM_w = {self.width_of_bim_graph} - Ширина графа\nL_w = {self.depth_of_bim_graph} - Глубина графа"