from dataclasses import dataclass
from enum import Enum, unique
from typing import Sequence
from uuid import UUID
import json

@dataclass(frozen=True)
class BPoint:
    x: float
    y: float
    z: float = 0.0

@unique
class BSign(Enum):
    DoorWay     = 0
    DoorWayInt  = 1
    DoorWayOut  = 2
    Room        = 3
    Staircase   = 4

    @classmethod
    def from_str(cls, name):
        return cls[name]

@dataclass(frozen=True)
class BBuildElement:
    id:     UUID
    sign:   BSign
    output: Sequence[UUID]
    points: Sequence[BPoint]
    name:   str     = ''
    sizeZ:  float   = 0.0


@dataclass(frozen=True)
class BLevel:
    name:       str
    elements:   Sequence[BBuildElement]
    zlevel:     float = 0.0


@dataclass(frozen=True)
class BBuilding:
    levels: Sequence[BLevel]
    name:   str
    addr:   str = ''


def mapping_building(file_buildingjson:str) -> BBuilding:
    building:BBuilding
    bad_elements = list()

    with open(file_buildingjson, 'r') as json_file:
        rjson = json.load(json_file)
        
        _levels = list()
        for level in rjson['Level']:
            _elements:Sequence[BBuildElement] = []
            for element in level['BuildElement']:
                _sign = BSign.from_str(element['Sign'])
                _sizeZ = element['SizeZ'] if not (_sign == BSign.DoorWay) else 0.0

                try:
                    build_element = BBuildElement(id=UUID(element['Id']),
                                                    sign=_sign,
                                                    name=element['Name'],
                                                    sizeZ=_sizeZ,
                                                    output=[UUID(uuid) for uuid in element['Output']],
                                                    points=[BPoint(p['x'], p['y'], level['ZLevel']) for p in element['XY'][0]['points']])
                    _elements.append(build_element)
                except:
                    bad_elements.append((_sign, element['Name'], element['Id'], level['ZLevel']))

            _levels.append(BLevel(name=level['NameLevel'], zlevel=level['ZLevel'], elements=_elements))

        building = BBuilding(name=rjson['NameBuilding'], levels=_levels)
    
    if len(bad_elements) > 0:
        import inspect
        print(f">UnknownException[{__file__}:{inspect.currentframe().f_lineno}]. Please check elements from list bellow:")
        for sign, name, id, level in bad_elements:
            print(f"{sign.name}({id}), name={name}, level={level})")
        print(">>QGIS expression for find bad elements (use 'Select Features Using Expression'):")
        print(' or '.join(f'id is \'{id}\'' for _,_,id,_ in bad_elements))
        exit()
    
    return building