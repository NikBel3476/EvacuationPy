import BimDataModel
from BimTools import Bim
from BimComplexity import BimComplexity

file = "building.json"

bim = Bim(BimDataModel.mapping_building(file))
bc  = BimComplexity(bim)

print(f"N_w = {bc.number_of_zones   } - Number of zones")
print(f"N_b = {bc.number_of_transits} - Number of transits")
print(f"M_w = {bc.width_of_bim_graph} - Width graph")
print(f"L_w = {bc.depth_of_bim_graph} - Depth graph")