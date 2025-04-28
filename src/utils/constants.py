from enum import Enum

class FACTIONS(str, Enum):
    ARTIFICERS = "artificers"
    OVERGROWTH = "overgrowth"
    REBEL = "rebel"
    NOCTURNE = "nocturne"

FACTIONS_ARR = [f.value for f in FACTIONS]