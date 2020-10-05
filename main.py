from network.model import Network
from time import perf_counter

tic = perf_counter()

network = Network("ProjectScheduler")

network.setCredentials('SUPERVISOR', 'ELECTRICITAN')

# WORKERS
network.addSource(ID='Person A', cost=100)
network.addSource('Person B', cost=100)
network.addSource('Person C', cost=150, creds={"ELECTRICITAN"})
network.addSource('Person D', cost=175, creds={"SUPERVISOR"})
network.addSource('Person E', cost=200, creds={"ELECTRICITAN", "SUPERVISOR"})
network.addSource('Person F', cost=250, creds={"ELECTRICITAN", "SUPERVISOR"})

# PROJECTS
network.addSink('Project A', capacityMin=1)
network.addSink('Project B', capacityMin=1, creds={"SUPERVISOR": 1})
network.addSink('Project C', capacityMin=2, capacityMax=2, creds={"SUPERVISOR": 1, "ELECTRICITAN": 1})

# EDGE CONSTRAINTS
## Enforce
#network.addEdgeConstraint("Person C", "Project A", mode=network.constraintMode.ENFORCE, category=network.edgeConstraintCategory.ACTIVE)
#network.addEdgeConstraint("Person D", "Project C", mode=network.constraintMode.ENFORCE, category=network.edgeConstraintCategory.ACTIVE)
#network.addEdgeConstraint("Person D", "Project A", mode=network.constraintMode.ENFORCE, category=network.edgeConstraintCategory.ACTIVE)
#network.addEdgeConstraint("Person C", "Project A", "enforce", "active")
## Request
#network.addEdgeConstraint("Person F", "Project B", mode="request", category=network.edgeConstraintCategory.ACTIVE)
#network.addEdgeConstraint("Person E", "Project A", "request", "inactive")

# RELATIONSHIPS
## Enforce
#network.addRelationship(sourceIDs={"Person B", "Person C"}, mode=network.constraintMode.ENFORCE, category=network.relationshipCategory.MATCH)
#network.addRelationship({"Person A", "Person E"}, mode="enforce", category="mismatch")
## Request
#network.addRelationship({"Person B", "Person C", "Person D"}, network.constraintMode.REQUEST, "match")
#network.addRelationship({"Person C", "Person D"}, "request", "mismatch")

status = network.solve(optSense="maximize", objectiveMode="requests")

#print(network._model)

print(status)
print(f"Objective value: {network._model.objective.value()}")
if status == 'Optimal':
    result = network.get_result()
    print()
    print(result.replace(0, ' '))


toc = perf_counter()
print(f"Execution time: {toc-tic:.2f} sec")