from enum import Enum

class ConstraintMode(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)
    REQUEST = "request"
    ENFORCE = "enforce"


class RelationshipCategory(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)
    MATCH = "match"
    MISMATCH = "mismatch"

class EdgeConstraintCategory(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)
    ACTIVE = "active"
    INACTIVE = "inactive"

class OptimizationSense(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"

class ObjectiveMode(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)
    NONE = "none"
    COST = "cost"
    REQUESTS = "requests"
    COSTANDREQUESTS = "cost+requests"