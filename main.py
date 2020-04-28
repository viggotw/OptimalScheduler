from base.nurse import Nurse
from base.shift import Shift, ShiftTypes

projects = {
    'Project 1': [Shift(1,1,1), Shift(1,1,1), Shift(1,1,1)],
    'Project 2': [Shift(1,1,1), Shift(1,1,1), Shift(1,1,1), Shift(1,1,1), Shift(1,1,1)]
}

employees = [Nurse(cost_per_shift=100,
                   overtime_cost_per_shift=150,
                   team_leader=False,
                   max_num_shifts=10,
                   min_num_shifts=2,
                   min_num_nightshift=1,
                   female=True),
             Nurse(cost_per_shift=100,
                   overtime_cost_per_shift=150,
                   team_leader=False,
                   max_num_shifts=10,
                   min_num_shifts=2,
                   min_num_nightshift=1,
                   female=False),
             Nurse(cost_per_shift=150,
                   overtime_cost_per_shift=200,
                   team_leader=True,
                   max_num_shifts=10,
                   min_num_shifts=2,
                   min_num_nightshift=1,
                   female=True),
             ]
