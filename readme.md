# Optimal Scheduler
This is a resource allocater. It enables you to find the *optimal* schedule that assigns resources (e.g. workers) to processes (e.g. projects or shifts). This is done by creating a so-called "graph" using Mixed-Integer Linear Programming, or MILP for short. This is a mathematical optimization aproach that ensures that the final schedule is the best of all possible schedules, according to your chosen objective funciton

## Example: Assign workers to projects
The `main.py` illustrates how one can use the networks-module create an optimal schedule for a company that has a work force that should be assigned to several projects. Note that this is just an example use case, and the module could also be used to e.g. assign nurses to shifts, or production orders to machines. This is further why the methods refers to "sources" and "sinks" rather than "workers" and "projects", following the terminology from graph theory.

### Create the network
First, create a network-object and give it a name, e.g. "ProjectScheduler". 
`network = Network("ProjectScheduler")`

### Create attributes
You have the option to specify certain attributes or roles for your resources. For workers, this could be e.g. "supervisor" or "head nurse", and is used to ensure that e.g. a shift always has enough resources with this attribute.
For our example, let's add create roles: supervisor and electrician
`network.setAttributes('SUPERVISOR', 'ELECTRICITAN')`

### Add workers
Workers can be added using the `addSource`-method. A source requires a unique name/ID. Additionally, you have the option to specify:
- `capacityMax` - maximum total projects/shifts
- `cost` - price to use this resource on a process (a project)
- `attrs` - a set that assigns the resource one or more attributes/roles

In our example, we add several workers. One of them is "Person C", which is an electrician that can work on maximum 1 project and will cost us $150.
`network.addSource('Person C', capacityMax=1, cost=150, attrs={"ELECTRICITAN"})`

### Add projects
Projects can be added using the `addSink`-method. A sink requires a unique name/ID. Additionally, you have the option to specify:
- capacityMin - minimum number of workers that this project requires
- capacityMax - maximum number of workers that this project requires
- attrs - a dictionary specifying the number of attributes/roles that are required for this project

In our example, we add three projects. One of them is "project C" that requires exactly 2 workers, and requires both a supervisor and an electrician. (note that a person that has both these roles could be used to cover both attribute requirements)
`network.addSink('Project C', capacityMin=2, capacityMax=2, attrs={"SUPERVISOR": 1, "ELECTRICITAN": 1})`

### Add constraints
A good schedule often needs to consider one or more constraints. The module supports some hard and soft constaints that are discussed below.

Note: The constaints has a `mode` and `category` parameter that accepts a predefined constant as input, like e.g. `network.relationshipCategory.MATCH`. These can also be appreviated as a string, like `"mismatch"`.

#### Enforce an assignment (hard constaint)
In some instances, you might want to ensure that a worker works on a specific project, or maybe that he *doesn't* work on a specific project. Such a constaint can be enforced as follows, where we e.g. want to enforce "Person B" to work on "Project B":
`network.addEdgeConstraint("Person B", "Project B", mode=network.constraintMode.ENFORCE, category=network.edgeConstraintCategory.ACTIVE)`

Alternativly, we could change the category-input to enforce that "Person B" does *not* work on "Project B as follows:
`network.addEdgeConstraint("Person B", "Project B", mode=network.constraintMode.ENFORCE, category=network.edgeConstraintCategory.INACTIVE)`

#### Enforce a team (hard constaint)
Some times, you might want to enforce that certain workers are assigned to the same project, or alternativly that they are *not* assigned to the same project. This can be be done as follows, where we e.g. want to enforce that "Person C" and "Person D" works together on the same project
`network.addRelationship(sourceIDs={"Person C", "Person D"}, mode=network.constraintMode.ENFORCE, category=network.relationshipCategory.MATCH)`

Alternativly, we could change the category-input to enforce that they do *not* work together:
`network.addRelationship(sourceIDs={"Person C", "Person D"}, mode=network.constraintMode.ENFORCE, category=network.relationshipCategory.MISMATCH)`

#### Request an assignment or a team (soft constaints)
In real world planning, you are often faces with requests that you would like to consider, but not be bound by. Some people might prefer to work together, and you would let them you could - but there might be a resource squeeze that makes the request impossible to fulfill. For these, softer constaints, you can change the constaint mode to `network.constraintMode.REQUEST` rather than `network.constraintMode.ENFORCE`. This further requires that you use an objective function that tries to optimize requests.

An example where we request that "Person B", "Person C" and "Person D" work together as a team will then look like
`network.addRelationship({"Person B", "Person C", "Person D"}, "request", "match")`

### Calculating the optimal schedule
Finally, we are ready to calculate the optimal schedule. This is done by solving the MILP problem, using the `solve`-method. This method has the following input parameters:
- `optSense` - should be minimize or maximize? This depends on your goal and the objective function being used. If you want to minimize cost, this should be "minimize". If you want to maximize happiness, this should be "maximize". If you want to do both, set it to "minimize".
- `objectibeMode` - this can be either "cost", "requests", "cost+requests" or "none". The first two are typically used to either only minimize cost or only maximize the number of requests. "cost+requests" requires an extra input `pricePerRequest`, and will try to find a schedule that both minimizes the cost and maximizes the number of fulfilled requests. "none" only requres that the constraints are satisfied, but has no objective function.
- `pricePerRequest` - This is the cost of not fulfilling a request. It is only required if `objectibeMode` is set to "cost+requests"

As an example, we would find the plan that minimizes the cost, but is penalized with a $500 fee for each request it does not fulfill
`status = network.solve(optSense="minimize", objectiveMode="cost+requests", pricePerRequest=500)`

To see the result, you can use e.g. the `getResult`-method, which will return a Pandas Dataframe that contains the final schedule.
`print(network.getResult())`

```
Example output:
Optimal
Objective value: 725.0
Total cost: 725.0
Happiness: -1
    > 0 requests accepted
    > 1 requests rejected

         Project A Project B Project C
Person A         1
Person B                             1
Person C         1
Person D                   1
Person E                             1
Person F
Execution time: 0.08 sec
```

## FAQ
### The status is "Infeasible"
There can be multiple reasons for this status, but in general it means that the requested schedule is impossible to calculate because of a combination of constraints. This typically occures if:
- You have either applied an impossible combination of "hard constraints" (e.g. "Worker A" should work on monday, and "Worker A" should *not* work on monday")
- You don't have enough sources (e.g. workers) to fulfill the number of sinks (e.g. projects)
- You don't have enough sources with the correct attributes (e.g. enough "electricians")