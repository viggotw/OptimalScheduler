from network.model import Network
from time import perf_counter

tic = perf_counter()

network = Network("ProjectScheduler")

network.setCredentials('SUPERVISOR', 'ELECTRICITAN')

network.addSource(id='Person A', cost=100)
network.addSource('Person B', cost=100)
network.addSource('Person C', cost=150, creds={"ELECTRICITAN"})
network.addSource('Person D', cost=175, creds={"SUPERVISOR"})
network.addSource('Person E', cost=200, creds={"ELECTRICITAN", "SUPERVISOR"})
network.addSource('Person F', cost=200, creds={"ELECTRICITAN", "SUPERVISOR"})

network.addSink('Project A', capacityMin=1)
network.addSink('Project B', capacityMin=1, creds={"SUPERVISOR": 1})
network.addSink('Project C', capacityMin=2, capacityMax=2, creds={"SUPERVISOR": 1, "ELECTRICITAN": 1})

network.addEdgeConstraint("Person A", "Project A", mode=network.constraintMode.ENFORCE, category=network.edgeConstraintCategory.INACTIVE)
network.addEdgeConstraint("Person C", "Project A", "enforce", "active")
#network.addEdgeConstraint("Person A", "Project C", mode="request", category=network.edgeConstraintCategory.ACTIVE)
#network.addEdgeConstraint("Person C", "Project B", "request", "inactive")

network.addRelationship(sourceIds={"Person B", "Person C"}, mode=network.constraintMode.ENFORCE, category=network.relationshipCategory.MATCH)
#network.addRelationship({"Person B", "Person C"}, mode="enforce", category="mismatch")
#network.addRelationship({"Person C", "Person D"}, network.constraintMode.REQUEST, "match")
#network.addRelationship({"Person D", "Person E"}, "request", "match")

status = network.solve(optSense="minimize", objectiveMode="cost")

#print(network._model)

print(status)
if status == 'Optimal':
    result = network.get_result()
    print(result)


toc = perf_counter()
print(f"Execution time: {toc-tic:.2f} sec")