import BimDataModel
from BimTools import Bim, Zone
from BimComplexity import BimComplexity
from BimEvac import Moving
from typing import List
import time
import asyncio


async def main() -> None:
    building = BimDataModel.mapping_building("resources/udsu_block_1.json")

    bim = Bim(building)
    BimComplexity(bim)  # check a building

    # Список комнат, не включающий безопасную зону
    wo_safety: List[Zone] = list(filter(lambda x: x.id != bim.safety_zone.id, bim.zones.values()))

    density = 0.1  # чел./м2
    bim.set_density(density)

    z: Zone
    for z in bim.zones.values():
        print(f"{z}, Количество человек: {z.num_of_people:.{4}}, Плотность: {z.density:.{4}} чел./м2")

    m = Moving()

    start = time.time()
    evacuation_time_in_minutes = 0.0  # Длительность эвакуации
    nop = sum([x.num_of_people for x in wo_safety if x.is_visited])
    while nop >= 10e-3:
        m.step(bim)
        evacuation_time_in_minutes += Moving.MODELLING_STEP
        # for z in bim.zones.values():
        #     print(f"{z}, Potential: {z.potential}, Number of people: {z.num_of_people}")
        # for t in bim.transits.values():
        #     if t.sign == BSign.DoorWayOut:
        #         pass
        # print(f"{t}, Number of people: {t.num_of_people}")

        nop = sum([x.num_of_people for x in wo_safety if x.is_visited])

        # print("========", nop, bim.safety_zone.num_of_people)
    end = time.time()

    print(f"Длительность эвакуации: {evacuation_time_in_minutes * 60:.2f} с. ({evacuation_time_in_minutes:.2f} мин.)")
    print(f"Количество людей: в здании -- {nop:.0f}, в безопасной зоне -- {bim.safety_zone.num_of_people:.0f} чел.")
    print(f"Время работы: {end - start:.3f} s")


if __name__ == "__main__":
    asyncio.run(main())
