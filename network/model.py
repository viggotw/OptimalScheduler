from enum import Enum
import pulp
import pandas as pd
import numpy as np
from .constants import ConstraintMode, RelationshipCategory, EdgeConstraintCategory, OptimizationSense, ObjectiveMode

class Source:  # "workers"
    def __init__(self, cost=None, *args):
        self.cost = float(cost)
        self.creds = set(args)  # "skills"


class Sink:  # "projects" or "shifts"
    def __init__(self, capacityMin, capacityMax, credentials={}):
        self.capacityMin = int(capacityMin)  # Number of workers
        self.capacityMax = capacityMax
        self.creds = credentials  # Required (number of) skills


class Relationship:
    def __init__(self, sourceIds, category):
        self.sourceIds = set(sourceIds)
        self.category = RelationshipCategory(category)


class Network:
    def __init__(self, name):
        self.sources = {}
        self.sinks = {}
        self.creds = None
        self._sources_with_creds = {}
        self.relationships = {ConstraintMode.ENFORCE: [], ConstraintMode.REQUEST: []}
        self.edgeConstraints = {ConstraintMode.ENFORCE: [], ConstraintMode.REQUEST: []}

        self._model = pulp.LpProblem(name, sense=pulp.LpMinimize)
        self._network = None
        self._constraints = []

        self.constraintMode = ConstraintMode
        self.relationshipCategory = RelationshipCategory
        self.edgeConstraintCategory = EdgeConstraintCategory

    def _get_enum_member(self, enum_member, enum):
        if isinstance(enum_member, str):
            assert enum_member in enum.__members__, f"{enum_member} is not a member of {enum} in {self}"
            member = enum.__members__[enum_member]
        elif enum_member in enum:
            member = enum_member
        else:
            raise TypeError(f"The credential {enum_member} must be either a string or an enum attribute member of {enum_member} in {self}")
        return member

    def setCredentials(self, *credentials):
        self.creds = set(credentials)
        self._sources_with_creds = {cred: [] for cred in self.creds}

    def addSource(self, id, cost, creds=set()):
        creds = set(creds)
        
        if creds and not self.creds:
            raise AttributeError("Object has no defined credentials. Use method .setCredentials() before adding sources with credentials.")
        
        credentials = set()
        for cred in creds:
            assert cred in self.creds
            self._sources_with_creds[cred].append(id)

        self.sources[id] = Source(cost, *credentials)

    def _get_enum_dict(self, orgDict):
        credsDict = {}
        for key in orgDict:
            key_enum = self._get_enum_member(key, self.creds)
            credsDict[key_enum] = orgDict[key]
        return credsDict

    def addSink(self, id, capacityMin=0, capacityMax=None, creds={}):
        for cred in creds:
            assert cred in self.creds
                
        self.sinks[id] = Sink(capacityMin, capacityMax, creds)

    def addRelationship(self, sourceIds, mode, category):
        sourceIds = set(sourceIds)
        mode = ConstraintMode(mode)
        category = RelationshipCategory(category)
        self.relationships[mode].append(Relationship(sourceIds, category))

    def addEdgeConstraint(self, sourceId, sinkId, mode, category):
        mode = ConstraintMode(mode)
        category = EdgeConstraintCategory(category)
        self.edgeConstraints[mode].append((sourceId, sinkId, category))

    def _build_network(self):
        data = {sink: {
            source : pulp.LpVariable(f"{source}_{sink}", cat="Binary") for source in self.sources.keys()}
            for sink in self.sinks.keys()}

        self._network = pd.DataFrame.from_dict(data)

    def _apply_source_capacity_constraints(self):
        for source_name, source in self.sources.items():
            self._model += (pulp.lpSum(self._network.loc[source_name, :].to_numpy()) <= 1,
                f"Maximum capacity for {source_name}")

    def _apply_sink_capacity_constraints(self):
        for sink_name, sink in self.sinks.items():
            self._model += (pulp.lpSum(self._network.loc[:,sink_name].to_numpy()) >= sink.capacityMin,
                f"Minimum capacity for {sink_name}")

            if sink.capacityMax:
                self._model += (pulp.lpSum(self._network.loc[:,sink_name].to_numpy()) <= sink.capacityMax,
                    f"Maximum capacity for {sink_name}")

    def _apply_sink_credential_constraints(self):
        for sink_name, sink in self.sinks.items():
            for cred in sink.creds:
                sources = self._sources_with_creds[cred]
                self._model += (pulp.lpSum(self._network.loc[sources,sink_name].to_numpy()) >= sink.creds[cred],
                f"Minimum credentials '{cred}' for {sink_name}")

    def _apply_source_relationships(self):
        for relationship in self.relationships[ConstraintMode.ENFORCE]:
            if relationship.category is RelationshipCategory.MATCH:
                for sink_name, sink in self.sinks.items():
                    sources2sink = self._network.loc[relationship.sourceIds, sink_name]
                    for (source1_name, source1_val), (source2_name, source2_val) in zip(sources2sink[:-1].items(), sources2sink[1:].items()):
                        self._model += (source1_val == source2_val,
                            f"Relatioship_match_{source1_name}_and_{source2_name}_for_{sink_name}")
            elif relationship.category is RelationshipCategory.MISMATCH:
                for sink_name, sink in self.sinks.items():
                    raise NotImplementedError()

        for relationship in self.relationships[ConstraintMode.REQUEST]:
            raise NotImplementedError()

    def _apply_edge_constraints(self):
        for sourceId, sinkId, category in self.edgeConstraints[ConstraintMode.ENFORCE]:
            if category is EdgeConstraintCategory.ACTIVE:
                self._model += self._network.loc[sourceId, sinkId] == 1
            elif category is EdgeConstraintCategory.INACTIVE:
                self._model += self._network.loc[sourceId, sinkId] == 0
            else:
                raise ValueError(f"Unrecognized edge constraint category '{category}' for the edge ({sourceId}, {sinkId})")

        for sourceId, sinkId, category in self.edgeConstraints[ConstraintMode.REQUEST]:
            raise NotImplementedError()

    def _set_objective(self, objective):
        if objective == ObjectiveMode.COST:
            obj_func = []
            for source_name, source in self.sources.items():
                source_cost = source.cost * pulp.lpSum(self._network.loc[source_name,:].to_numpy()) 
                obj_func.append(source_cost)

            self._model += pulp.lpSum([obj_func])

        elif objective == ObjectiveMode.REQUESTS:
            raise NotImplementedError()

    def _get_vals(self, x):
        if isinstance(x, pulp.pulp.LpVariable):
            val = x.value()
            if val is None:
                return None
            elif 0 < abs(val) < 1e-6:
                # Use threshold to cap off rounding errors for binary variables
                return 0
            else:
                return val
        elif np.isnan(x):
            return x
        else:
            return x

    def _get_cost(self, result):
        cost = 0
        for source_name, source in self.sources.items():
            cost += source.cost * result.loc[source_name,:].sum()
        return cost

    def _apply_constraints(self):
        self._apply_source_capacity_constraints()
        self._apply_sink_capacity_constraints()
        self._apply_sink_credential_constraints()
        self._apply_edge_constraints()
        self._apply_source_relationships()
    

    def solve(self, optSense="minimize", objectiveMode="cost"):
        objectiveMode = ObjectiveMode(objectiveMode)
        sense = OptimizationSense(optSense)

        if optSense is OptimizationSense.MAXIMIZE:
            self._model.objective.sense = pulp.LpMaximize
        elif optSense is OptimizationSense.MINIMIZE:
            self._model.objective.sense = pulp.LpMinimize

        self._build_network()
        self._apply_constraints()
        self._set_objective(objectiveMode)

        status = self._model.solve()
        return pulp.LpStatus[status]


    def get_result(self):
        result = self._network.copy(deep=True)
        result = result.applymap(self._get_vals)

        cost = self._get_cost(result)

        print(f"Total cost: {cost}")

        return result.astype(int)
