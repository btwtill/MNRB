from enum import Enum
#re-exported so importers of this module get it alongside the enums
from MNRB.ROSE_Data.rose_enum import enumValue #type: ignore

class ConstraintType(Enum):
    """How a constraint is realised in Maya.

    Values are used in serialization, so they must stay stable.
    """

    #a multMatrix/decompose network - no constraint node, evaluates cheaply, and
    #leaves the channel box clean
    MATRIX = "matrix"
    #Maya's own constraint nodes - familiar to anyone opening the rig outside
    #ROSE, and what to fall back to when something misbehaves
    NATIVE = "native"

class ConstraintKind(Enum):
    """What a constraint constrains. Same meaning in either type."""

    PARENT = "parent"
    POINT = "point"
    ORIENT = "orient"
    SCALE = "scale"
    AIM = "aim"

def mapNameToConstraintType(type_name):
    #tolerates being handed a member instead of a name, including a stale one
    type_name = enumValue(type_name)
    for constraint_type in ConstraintType:
        if constraint_type.value == type_name:
            return constraint_type
    return ConstraintType.MATRIX

def mapNameToConstraintKind(kind_name):
    #tolerates being handed a member instead of a name, including a stale one
    kind_name = enumValue(kind_name)
    for constraint_kind in ConstraintKind:
        if constraint_kind.value == kind_name:
            return constraint_kind
    return ConstraintKind.PARENT
