from enum import Enum

class RelationshipCategory(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)
    MATCH = "match"
    MISMATCH = "mismatch"


class RelationshipMode(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)
    REQUEST = "request"
    ENFORCE = "enforce"


class EdgeConstraintMode(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)
    REQUEST_TRUE = "request true"
    REQUEST_FALSE = "request false"
    ENFORCE_TRUE = "enforce true"
    ENFORCE_FALSE = "enforce false"

