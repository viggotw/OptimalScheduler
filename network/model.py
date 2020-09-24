from .constants import RelationshipCategory, RelationshipMode, EdgeConstraintMode

class Source:  # "workers"
    def __init__(self, id, name, cost=None, attributes=set()):
        self.id = int(id)
        self.name = str(name)
        self.attributes = set(attributes)  # "skills"
        self.cost = float(cost)


class Sink:  # "projects" or "shifts"
    def __init__(self, id, name, capacityMin, capacityMax, attributesMin={}, attributesMax={}):
        self.id = int(id)
        self.name = str(name)
        self.capacityMin = int(capacityMin)  # Number of workers
        self.capacityMax = int(capacityMax)
        self.attributesMin = dict(attributesMin)  # Required (number of) skills
        self.attributesMax = dict(attributesMax)


class Relationship:
    def __init__(self, id, name, category, mode, sourceIds=[]):
        self.name = str(name)
        self.category = RelationshipCategory(category)
        self.mode = RelationshipMode(mode)
        self.sourceIds = sourceIds


class EdgeConstraint:
    def __init__(self, sourceId, sinkId, mode):
        self.sourceId = int(sourceId)
        self.sinkId = int(sinkId)
        self.mode = EdgeConstraintMode(mode)


class Network:
    def __init__(self):
        self.sources = {}
        self.sinks = {}
        self.relationships = []
        self.edgeConstraints = {}
        self._network = None

    def addSource(self, id, name, cost, attributes):
        self.sources[id] = Source(id, name, cost, attributes)

    def addSink(self, id, name, capacityMin, capacityMax, attributesMin, attributesMax):
        self.sinks[id] = Sink(id, name, capacityMin, capacityMax, attributesMin, attributesMax)

    def addRelationship(self, id, name, category, mode, sourceIds):
        self.relationships.append(Relationship(id, name, category, mode, sourceIds))

    def addEdgeConstraint(self, sourceId, sinkId, mode):
        self.edgeConstraints = EdgeConstraint(sourceId, sinkId, mode)

    def solve(self):
        print("Solve")
