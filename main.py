import BimDataModel
from BimTools import Bim
from BimComplexity import BimComplexity
from BimEvac import Moving

building = BimDataModel.mapping_building('resources/example-one-exit.json')
# building = BimDataModel.mapping_building('resources/building_example.json')

bim = Bim(building)

BimComplexity(bim) # check a building

m = Moving()

m.step(bim)