import pandas as pd

PATH_LISTS = "init\google sheet csv input\Optimal Project Resource Scheduler - Lists.csv"
PATH_MATCHES = "init\google sheet csv input\Optimal Project Resource Scheduler - Matches and mismatches.csv"
PATH_PROJECTS = "init\google sheet csv input\Optimal Project Resource Scheduler - Projects.csv"
PATH_SHIFT_REQUESTS = "init\google sheet csv input\Optimal Project Resource Scheduler - Worker shift requests.csv"
PATH_WORKERS = "init\google sheet csv input\Optimal Project Resource Scheduler - Workers.csv"

lists_df = pd.read_csv(PATH_LISTS, header=1)

optimization_mode_types = lists_df.iloc[:,0].dropna()
type_match = lists_df.iloc[:,3].dropna()
type_worker_skill = lists_df.iloc[:,1].dropna()
type_worker_relationship = lists_df.iloc[:,2].dropna()
type_worker_shift_request = lists_df.iloc[:,4].dropna()

matches_df = pd.read_csv(PATH_MATCHES, header=1, index_col=0).T

