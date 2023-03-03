import BimDataModel
from BimTools import Bim, Transit, Zone
from BimComplexity import BimComplexity

building = BimDataModel.mapping_building('resources/cfast-learn_2d.json')
# building = BimDataModel.mapping_building('resources/building_example.json')

bim = Bim(building)

bc = BimComplexity(bim)
print(bc)


