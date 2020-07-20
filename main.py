import json
import pulp
import pandas as pd
import numpy as np

with open("init/request.json", "r") as f:
    input_dict = json.loads(f.read())

general_rules = input_dict["general rules"]
shift_info = input_dict["shift_info"]
schedule = input_dict["schedule"]
employees = input_dict['employees']

# Insert default values
for id, employee in input_dict['employees'].items():
    if 'supervisor' not in employee:
        employees[id]['supervisor'] = False

    if 'custom rules' not in employee:
        employees[id]['custom rules'] = []

supervisors = [emp_id for emp_id in employees  if employees[emp_id]["supervisor"]]

shift_vars = {}
for emp_id, emp in employees.items():
    shift_vars[emp_id] = {}
    for day in schedule:
        for shift in schedule[day]:
            shift_vars[emp_id][(day, shift)] = pulp.LpVariable(f"{emp_id}_{day}_{shift}", cat="Binary")
    
    for custom_rule in emp["custom rules"]:
        if custom_rule["rule"] == "require work":
            shift_vars[emp_id][(custom_rule["day"], custom_rule["shift"])] = 1
        elif custom_rule["rule"] == "require free":
            shift_vars[emp_id][(custom_rule["day"], custom_rule["shift"])] = 0
        else:
            raise ValueError(f"Unknown custom rule for {emp_id}: {custom_rule['rule']}")


df = pd.DataFrame.from_dict(shift_vars, orient='index')

model = pulp.LpProblem("NurseScheduling", sense=pulp.LpMinimize)

# Source node constraints
for emp_name, emp_info in employees.items():
    ## Restrain minimum number of shifts per employee
    model += pulp.lpSum(df.loc[emp_name]) >= emp_info["shifts normal"], f"Min shifts for {emp_name}"

    ## Restrain maximum number of shifts per employee
    model += pulp.lpSum(df.loc[emp_name]) <= emp_info["shifts max"], f"Max shifts for {emp_name}"

# Sink node constraints
for day in schedule:
    for shift_name in schedule[day]:
        ## Restrain minimum number of workers
        model += pulp.lpSum(df.loc[:, (day, shift_name)]) >= shift_info[shift_name]["num workers min"], f"Min workers for {day} {shift_name}"

        ## Restrain maximum number of workers
        model += pulp.lpSum(df.loc[:, (day, shift_name)]) <= shift_info[shift_name]["num workers max"], f"Max workers for {day} {shift_name}"

## Restrain each morning shift to always have minimum one "supervisor"
morning_shifts = [item for item in df.columns if item[1] == "morning"]
for morning_shift in morning_shifts:
    model += pulp.lpSum(df.loc[supervisors, morning_shift]) >= 1, f"Morning shift on {morning_shift[0]} has at least one supervisor"

shift_hours = np.array([shift_info[shift]['duration hours'] for day in schedule for shift in schedule[day]])

for emp in employees:
    # Restrain maximum consecutive shifts
    max_shifts = general_rules["shifts max consecutive"]
    shifts = df.loc[emp].index.to_list()
    N = df.shape[1]
    
    start = range(N-max_shifts-1)
    end = range(max_shifts+1, N)
    
    for s, e in zip(start, end):
        model += pulp.lpSum(df.loc[emp].iloc[s:e]) <= max_shifts, f"Consecutive shift limit for {emp} in range {shifts[s]} to {shifts[e-1]}"

    # Restrain maximum allowed working hours
    total_hours = 0
    for day in schedule:
        for shift_name in schedule[day]:
            total_hours += 0

    model += pulp.lpSum(shift_hours * df.loc[emp]) <= general_rules['hours max']

# Objective function
total_cost_normal = 0
total_cost_overtime = 0
for emp_name, emp_info in employees.items():
    ## Restrain minimum number of shifts per employee
    total_cost_normal += pulp.lpSum(df.loc[emp_name]) * emp_info["cost normal"]
    total_cost_overtime += (pulp.lpSum(df.loc[emp_name]) - emp_info["shifts normal"]) * emp_info["cost overtime"]

model += total_cost_normal + total_cost_overtime

status = model.solve()

df_values = df.applymap(lambda x: bool(x.value()) if isinstance(x, pulp.LpVariable) else bool(x))
df_values = df_values.append(df_values.sum(axis=0).rename("SUM"))

print(f"STATUS: {pulp.LpStatus[status]}")
print()
print("OPTIMAL SCHEDULE")
print(df_values)
print()
print(f"Total price: {model.objective.value():,.2f} NOK")
df_values.to_csv("Optimal Schedule.csv")
