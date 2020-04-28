class Nurse:
    def __init__(self, cost_per_shift, overtime_cost_per_shift, team_leader, max_num_shifts, min_num_shifts, min_num_nightshift, female):
        self.cost_per_shift = cost_per_shift
        self.overtime_cost_per_shift = overtime_cost_per_shift
        self.team_leader = team_leader
        self.max_num_shifts = max_num_shifts
        self.min_num_shifts = min_num_shifts
        self.min_num_nightshift = min_num_nightshift
        self.female = female

        # todo: Add attribute for "Minimum number of shifts of type (j) that a head nurse should work."