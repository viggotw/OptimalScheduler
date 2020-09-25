from enum import Enum
from .constants import RelationshipCategory, RelationshipMode, EdgeConstraintMode

class Source:  # "workers"
    def __init__(self, id, name, cost=None, *args):
        self.id = int(id)
        self.name = str(name)
        self.cost = float(cost)
        self.creds = set(args)  # "skills"


class Sink:  # "projects" or "shifts"
    def __init__(self, id, name, capacityMin, capacityMax, credentials={}):
        self.id = int(id)
        self.name = str(name)
        self.capacityMin = int(capacityMin)  # Number of workers
        self.capacityMax = capacityMax
        self.creds = credentials  # Required (number of) skills


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
        self.creds = None
        self.relationships = []
        self.edgeConstraints = {}
        self._network = None

    def setCredentials(self, *sequential, **named):
        enums = dict(zip(sequential, range(len(sequential))), **named)
        self.creds = Enum("Credential", enums)

    def _get_enum_credential(self, cred):
        if isinstance(cred, str):
            assert cred in self.creds.__members__, f"{cred} is not a member of {self.creds} in {self}"
            cred_enum = self.creds.__members__[cred]
        elif cred in self.creds:
            cred_enum = cred
        else:
            raise TypeError(f"The credential {cred} must be either a string or an enum attribute member of {self.creds} in {self}")
        return cred_enum
        
    
    def addSource(self, id, name, cost, creds=set()):
        creds = set(creds)
        
        if creds and not self.creds:
            raise AttributeError("Object has no defined credentials. Use method .setCredentials() before adding sources with credentials.")
        
        credentials = set()
        for cred in creds:
            cred_enum = self._get_enum_credential(cred)
            credentials.add(cred_enum)

        self.sources[id] = Source(id, name, cost, *credentials)

    def _get_enum_dict(self, orgDict):
        credsDict = {}
        for key in orgDict:
            key_enum = self._get_enum_credential(key)
            credsDict[key_enum] = orgDict[key]
        return credsDict

    def addSink(self, id, name, capacityMin=0, capacityMax=None, credentials=None):
        if credentials:
            credentials = self._get_enum_dict(credentials)
                
        self.sinks[id] = Sink(id, name, capacityMin, capacityMax, credentials)

    def addRelationship(self, id, name, category, mode, sourceIds):
        self.relationships.append(Relationship(id, name, category, mode, sourceIds))

    def addEdgeConstraint(self, sourceId, sinkId, mode):
        self.edgeConstraints = EdgeConstraint(sourceId, sinkId, mode)

    def solve(self):
        print("Solve")
