from enum import Enum


class ShiftTypes(Enum):
    morning = 0
    afternoon = 1
    night_weekday = 2
    night_weekend1 = 3
    night_weekend2 = 4


class Shift:
    def __init__(self, num_required_staff, shift_type, shift_length):
        if not isinstance(shift_type, ShiftTypes):
            raise ValueError(f"shift_type must be of type {ShiftTypes}, not {type(shift_type)}")

        self.num_required_staff = num_required_staff
        self.type = shift_type
        self.shift_length = shift_length


class ShiftRules:
    pass
    # If a nurse has a shift in a specific day, then, he/she should be
    # off for next two consecutive shifts. However, if a nurse has
    # two consecutive shifts in a specific day, he/she should be off
    # for next three consecutive shifts.

