from enum import Enum
from collections import OrderedDict
import pulp
import pandas as pd
import numpy as np
from .constants import ConstraintMode, RelationshipCategory, EdgeConstraintCategory, OptimizationSense, ObjectiveMode

class Source:  # "workers"
    def __init__(self, capacityMin=0, capacityMax=None, cost=0, *args):

        self.capacityMin = int(capacityMin)
        if capacityMax:
            self.capacityMax = int(capacityMax)
        self.cost = float(cost)
        self.attrs = set(args)  # "skills"


class Sink:  # "projects" or "shifts"
    def __init__(self, capacityMin, capacityMax, attributes={}):
        self.capacityMin = int(capacityMin)  # Number of workers
        self.capacityMax = capacityMax
        self.attrs = attributes  # Required (number of) skills


class Relationship:
    def __init__(self, sourceIDs, category):
        self.sourceIDs = set(sourceIDs)
        self.category = RelationshipCategory(category)


class Network:
    def __init__(self, name):
        self.name = name
        self.sources = {}
        self.sinks = {}
        self.attrs = None
        self._sourcesWithAttrs = {}
        self.relationships = {ConstraintMode.ENFORCE: [], ConstraintMode.REQUEST: []}
        self.edgeConstraints = {ConstraintMode.ENFORCE: [], ConstraintMode.REQUEST: []}

        self._model = None
        self._constraints = OrderedDict()
        self._relationshipVars = {}
        self._objFuncRequestTerms = []
        self._network = None

        self.constraintMode = ConstraintMode
        self.relationshipCategory = RelationshipCategory
        self.edgeConstraintCategory = EdgeConstraintCategory

    def _getEnumMember(self, enum_member, enum):
        if isinstance(enum_member, str):
            assert enum_member in enum.__members__, f"{enum_member} is not a member of {enum} in {self}"
            member = enum.__members__[enum_member]
        elif enum_member in enum:
            member = enum_member
        else:
            raise TypeError(f"The attribute {enum_member} must be either a string or an enum attribute member of {enum_member} in {self}")
        return member

    def setAttributes(self, *attributes):
        self.attrs = set(attributes)
        self._sourcesWithAttrs = {attr: [] for attr in self.attrs}

    def addSource(self, ID, capacityMin=0, capacityMax=None, cost=0, attrs=set()):
        attrs = set(attrs)
        
        if attrs and not self.attrs:
            raise AttributeError("Object has no defined attributes. Use method .setAttributes() before adding sources with attributes.")
        
        attributes = set()
        for attr in attrs:
            assert attr in self.attrs
            self._sourcesWithAttrs[attr].append(ID)

        self.sources[ID] = Source(capacityMin, capacityMax, cost, *attributes)

    def _getEnumDict(self, orgDict):
        attrsDict = {}
        for key in orgDict:
            key_enum = self._getEnumMember(key, self.attrs)
            attrsDict[key_enum] = orgDict[key]
        return attrsDict

    def addSink(self, ID, capacityMin=0, capacityMax=None, attrs={}):
        for attr in attrs:
            assert attr in self.attrs
                
        self.sinks[ID] = Sink(capacityMin, capacityMax, attrs)

    def addRelationship(self, sourceIDs, mode, category):
        sourceIDs = set(sourceIDs)
        mode = ConstraintMode(mode)
        category = RelationshipCategory(category)
        self.relationships[mode].append(Relationship(sourceIDs, category))

    def addEdgeConstraint(self, sourceID, sinkID, mode, category):
        mode = ConstraintMode(mode)
        category = EdgeConstraintCategory(category)
        self.edgeConstraints[mode].append((sourceID, sinkID, category))

    def _buildNetwork(self):
        data = {sink: {
            source : pulp.LpVariable(f"{source}_{sink}", cat="Binary") for source in self.sources.keys()}
            for sink in self.sinks.keys()}

        self._network = pd.DataFrame.from_dict(data)

    def _constrainSourceCapacities(self):
        for sourceName, source in self.sources.items():
            self._constraints[f"Minimum capacity for {sourceName}"] = \
                 pulp.lpSum(self._network.loc[sourceName, :].to_numpy()) >= source.capacityMin
            
            self._constraints[f"Maximum capacity for {sourceName}"] = \
                 pulp.lpSum(self._network.loc[sourceName, :].to_numpy()) <= source.capacityMax

    def _constrainSinkCapacities(self):
        for sinkName, sink in self.sinks.items():
            self._constraints[f"Minimum capacity for {sinkName}"] = \
                pulp.lpSum(self._network.loc[:,sinkName].to_numpy()) >= sink.capacityMin

            if sink.capacityMax:
                self._constraints[f"Maximum capacity for {sinkName}"] = \
                    pulp.lpSum(self._network.loc[:,sinkName].to_numpy()) <= sink.capacityMax

    def _constrainSinkAttributes(self):
        for sinkName, sink in self.sinks.items():
            for attr in sink.attrs:
                sources = self._sourcesWithAttrs[attr]
                self._constraints[f"Minimum attributes '{attr}' for {sinkName}"] = \
                    pulp.lpSum(self._network.loc[sources,sinkName].to_numpy()) >= sink.attrs[attr]

    def _constrainEdges(self):
        # Force specific source and sink to be either active or inactive
        for sourceID, sinkID, category in self.edgeConstraints[ConstraintMode.ENFORCE]:
            if category is EdgeConstraintCategory.ACTIVE:
                self._constraints[f"Force {sourceID} to be active for {sinkID}"] = self._network.loc[sourceID, sinkID] == 1
            
            elif category is EdgeConstraintCategory.INACTIVE:
                self._constraints[f"Force {sourceID} to be inactive for {sinkID}"] = self._network.loc[sourceID, sinkID] == 0
            
            else:
                raise ValueError(f"Unrecognized edge constraint category '{category}' for the edge ({sourceID}, {sinkID})")

        # Request specific source and sink to be either active or inactive
        for sourceID, sinkID, category in self.edgeConstraints[ConstraintMode.REQUEST]:
            if category is EdgeConstraintCategory.ACTIVE:
                self._objFuncRequestTerms.append(
                    self._network.loc[sourceID, sinkID]
                )
            elif category is EdgeConstraintCategory.INACTIVE:
                self._objFuncRequestTerms.append(
                    -self._network.loc[sourceID, sinkID]
                )
            else:
                raise ValueError(f"Unrecognized edge constraint category '{category}' for the edge ({sourceID}, {sinkID})")

    def _constrainSourceRelationships(self):
        # Force relationship into a match or mistmatch
        for relationship in self.relationships[ConstraintMode.ENFORCE]:
            if relationship.category is RelationshipCategory.MATCH:
                for sinkName in self.sinks:
                    sources2sink = self._network.loc[relationship.sourceIDs, sinkName]
                    for (source1_name, source1_var), (source2_name, source2_var) in zip(sources2sink[:-1].items(), sources2sink[1:].items()):
                        self._constraints[f"Relatioship_match_{source1_name}_and_{source2_name}_for_{sinkName}"] = \
                            source1_var == source2_var
            elif relationship.category is RelationshipCategory.MISMATCH:
                for sinkName in self.sinks:
                    sources2sink = self._network.loc[relationship.sourceIDs, sinkName]
                    for (source1_name, source1_var), (source2_name, source2_var) in zip(sources2sink[:-1].items(), sources2sink[1:].items()):
                        self._constraints[f"Relatioship_mismatch_{source1_name}_and_{source2_name}_for_{sinkName}"] = \
                            source1_var + source2_var <= 1

        # Request relationship into a match or mistmatch
        for relationship in self.relationships[ConstraintMode.REQUEST]:
            if relationship.category is RelationshipCategory.MATCH:
                sourceIDsTxt = str(relationship.sourceIDs).replace(' ','')
                for sinkName in self.sinks:
                    relationshipMatch = pulp.LpVariable(f"relationshipMatch_{sourceIDsTxt}_{sinkName}", upBound=1)
                    sources2sink = self._network.loc[relationship.sourceIDs, sinkName]

                    for i, source2sink in enumerate(sources2sink):
                        self._constraints[f"RelationshipMatch_{relationship.sourceIDs}_to_{sinkName}_#{i+1}"] = \
                        relationshipMatch <= source2sink

                    self._relationshipVars[str(relationshipMatch)] = relationshipMatch
                    self._objFuncRequestTerms.append(relationshipMatch)

            elif relationship.category is RelationshipCategory.MISMATCH:
                sourceIDsTxt = str(relationship.sourceIDs).replace(' ','')
                for sinkName in self.sinks:
                    relationshipMismatch = pulp.LpVariable(f"relationshipMismatch_{sourceIDsTxt}_{sinkName}", lowBound=0)
                    sources2sink = self._network.loc[relationship.sourceIDs, sinkName]

                    self._constraints[f"Relatioship_mismatch_{sourceIDsTxt}_for_{sinkName}"] = \
                        relationshipMismatch >= pulp.lpSum(sources2sink) - (len(sources2sink) - 1)

                    self._relationshipVars[str(relationshipMismatch)] = relationshipMismatch
                    self._objFuncRequestTerms.append(-relationshipMismatch)

    def _getObjectiveCostTerms(self):
        objFuncList = []
        for sourceName, source in self.sources.items():
            sourceCost = source.cost * pulp.lpSum(self._network.loc[sourceName,:].to_numpy()) 
            objFuncList.append(sourceCost)
        return objFuncList

    def _getValues(self, x):
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

    def _getTotalCost(self, result):
        cost = 0
        for sourceName, source in self.sources.items():
            cost += source.cost * result.loc[sourceName,:].sum()
        return cost

    def _getRequestScores(self, results):
        score_requests_accepted = 0
        score_requests_rejected = 0

        # Count accepted edge requests
        for sourceID, sinkID, category in self.edgeConstraints[ConstraintMode.REQUEST]:
            if (category is EdgeConstraintCategory.ACTIVE and results.loc[sourceID, sinkID] == 1) or \
               (category is EdgeConstraintCategory.INACTIVE and results.loc[sourceID, sinkID] == 0):
               score_requests_accepted += 1

            elif (category is EdgeConstraintCategory.ACTIVE and results.loc[sourceID, sinkID] == 0) or \
                 (category is EdgeConstraintCategory.INACTIVE and results.loc[sourceID, sinkID] == 1):
                score_requests_rejected += 1

        # Count accepted relationship requests
        for relationship in self.relationships[ConstraintMode.REQUEST]:
            if (relationship.category is RelationshipCategory.MATCH and results.loc[relationship.sourceIDs].prod().max() == 1) or \
               (relationship.category is RelationshipCategory.MISMATCH and results.loc[relationship.sourceIDs].prod().max() == 0) :
                score_requests_accepted += 1
            elif (relationship.category is RelationshipCategory.MATCH and results.loc[relationship.sourceIDs].prod().max() == 0) or \
                 (relationship.category is RelationshipCategory.MISMATCH and results.loc[relationship.sourceIDs].prod().max() == 1) :
                score_requests_rejected += 1

        return score_requests_accepted, score_requests_rejected

    def _setConstraints(self):
        self._constrainSourceCapacities()
        self._constrainSinkCapacities()
        self._constrainSinkAttributes()
        self._constrainEdges()
        self._constrainSourceRelationships()  

        self._model.constraints = self._constraints  

    def _setObjective(self, objective, pricePerRequest=0):
        objective = ObjectiveMode(objective)

        if objective == ObjectiveMode.COST:
            objCostTerms = self._getObjectiveCostTerms()
            self._model.objective = pulp.lpSum(objCostTerms)

        elif objective == ObjectiveMode.REQUESTS:
            self._model.objective = pulp.lpSum(self._objFuncRequestTerms)

        elif objective == ObjectiveMode.COSTANDREQUESTS:
            objCostTerms = self._getObjectiveCostTerms()
            objRequestTerms = self._objFuncRequestTerms
            self._model.objective = pulp.lpSum(objCostTerms) - pricePerRequest * pulp.lpSum(objRequestTerms)

        elif objective == ObjectiveMode.NONE:
            self._model.objective = 0

    def solve(self, optSense="minimize", objectiveMode="cost", pricePerRequest=0, **kwargs):
        optSense = OptimizationSense(optSense)

        if optSense is OptimizationSense.MAXIMIZE:
            sense = pulp.LpMaximize
        elif optSense is OptimizationSense.MINIMIZE:
            sense = pulp.LpMinimize

        self._model = pulp.LpProblem(self.name, sense=sense)
        self._buildNetwork()
        self._setConstraints()
        self._setObjective(objectiveMode, pricePerRequest)

        self._model.solver = pulp.apis.PULP_CBC_CMD(**kwargs)
        status = self._model.solve()
        return pulp.LpStatus[status]

    def getResult(self):
        result = self._network.copy(deep=True)
        result = result.applymap(self._getValues).astype(int)

        total_cost = self._getTotalCost(result)
        score_requests_accepted, score_requests_rejected = self._getRequestScores(result)

        print(f"Total cost: {total_cost}")
        print(f'Happiness: {score_requests_accepted - score_requests_rejected}')
        print(f"    > {score_requests_accepted} requests accepted")
        print(f"    > {score_requests_rejected} requests rejected")

        return result
