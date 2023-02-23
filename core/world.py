import dataclasses
from .geometry import Segment
from typing import List

@dataclasses.dataclass
class World():
    walls: List[Segment]

def MakeWorld() -> World:
    return World([])