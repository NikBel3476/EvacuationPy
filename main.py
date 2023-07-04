import BimDataModel
from BimTools import Bim, Zone
from BimComplexity import BimComplexity
from BimEvac import Moving
from BimDataModel import BSign
from typing import List

building = BimDataModel.mapping_building("resources/example-two-exits.json")

bim = Bim(building)
BimComplexity(bim)  # check a building

# Список комнат, не включающий безопасную зону
wo_safety: List[Zone] = list(filter(lambda x: not (x.id == bim.safety_zone.id), bim.zones.values()))

density = 1.0  # чел./м2
bim.set_density(density)

z: Zone
for z in bim.zones.values():
    print(f"{z}, Количество человек: {z.num_of_people:.{4}}, Плотность: {z.density:.{4}} чел./м2")

m = Moving()

time = 0.0  # Длительность эвакуации
for _ in range(1000):
    m.step(bim)
    time += Moving.MODELLING_STEP
    # for z in bim.zones.values():
    #     print(f"{z}, Potential: {z.potential}, Number of people: {z.num_of_people}")
    for t in bim.transits.values():
        if t.sign == BSign.DoorWayOut:
            pass
            # print(f"{t}, Number of people: {t.num_of_people}")

    nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
    if nop < 10e-3:
        break

    # print("========", nop, bim.safety_zone.num_of_people)

print(f"Длительность эвакуации: {time*60:.{4}} с. ({time:.{4}} мин.)")
nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
print(f"Количество людей: в здании -- {nop:.{4}}, в безопасной зоне -- {bim.safety_zone.num_of_people:.{4}} чел.")
