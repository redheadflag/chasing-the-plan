from __future__ import annotations

import enum


class DayOfWeek(str, enum.Enum):
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"
    SAT = "SAT"
    SUN = "SUN"


class WorkoutKind(str, enum.Enum):
    """Which flavour of workout the coach is building."""

    ORDINARY = "ORDINARY"
    SUPERSET_BASED = "SUPERSET_BASED"


class BlockType(str, enum.Enum):
    """A block is either one standalone exercise or a superset of several."""

    SINGLE = "SINGLE"
    SUPERSET = "SUPERSET"


class PlanExerciseKind(str, enum.Enum):
    WEIGHT = "WEIGHT"
    TIME = "TIME"
