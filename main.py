import BimDataModel
from BimTools import Bim
from BimComplexity import BimComplexity

building = BimDataModel.mapping_building('resources/cfast-learn-2d.json')
# building = BimDataModel.mapping_building('resources/building_example.json')

bim = Bim(building)

bc = BimComplexity(bim)
print(bc)