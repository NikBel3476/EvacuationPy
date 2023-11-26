import asyncio
import time
from typing import List

import BimDataModel
from BimComplexity import BimComplexity
from BimEvac import Moving
from BimTools import Bim, Zone


async def main() -> None:
    building = BimDataModel.mapping_building("resources/disbuild.json")

    bim = Bim(building)
    BimComplexity(bim)  # check a building

    m = Moving(bim)

    # Список комнат, не включающий безопасную зону
    # wo_safety: List[Zone] = list(filter(lambda x: x.id != m.bim.safety_zone.id, m.bim.zones.values()))
    wo_safety: List[Zone] = m.building_zones()

    density = 1.0  # чел./м2
    bim.set_density(density)

    z: Zone
    for z in bim.zones.values():
        print(f"{z}, Количество человек: {z.num_of_people:.{4}}, Плотность: {z.density:.{4}} чел./м2")

    start = time.time()
    nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
    while nop >= 10e-3:
        m.step()
        # for z in bim.zones.values():
        #     print(f"{z}, Potential: {z.potential}, Number of people: {z.num_of_people}")
        # for t in bim.transits.values():
        #     if t.sign == BSign.DoorWayOut:
        #         pass
        # print(f"{t}, Number of people: {t.num_of_people}")

        nop = sum([x.num_of_people for x in wo_safety if x.is_visited])

        # print("========", nop, bim.safety_zone.num_of_people)
    end = time.time()

    print(f"Длительность эвакуации: {m.time_in_minutes * 60:.2f} с. ({m.time_in_minutes:.2f} мин.)")
    print(f"Количество людей: в здании -- {nop:.2f}, в безопасной зоне -- {bim.safety_zone.num_of_people:.2f} чел.")
    print(f"Время работы: {end - start:.3f} s")


if __name__ == "__main__":
    asyncio.run(main())
