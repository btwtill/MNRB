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

class ConstraintChannels:
    """Which axes of which channels a constraint is allowed to drive.

    Narrows a kind rather than replacing it: a point constraint handed rotate
    axes still drives no rotation. Full - the default - means the constraint
    behaves exactly as it did before masks existed.

    Axes are kept as strings ("XZ"), which is also how they serialize.
    """

    CHANNELS = ("translate", "rotate", "scale")
    AXES = "XYZ"

    def __init__(self, translate = "XYZ", rotate = "XYZ", scale = "XYZ"):
        self.axes = {"translate": self.cleanAxes(translate),
                     "rotate": self.cleanAxes(rotate),
                     "scale": self.cleanAxes(scale)}

    @classmethod
    def cleanAxes(cls, axes):
        #always in XYZ order, so two masks with the same axes compare equal
        return "".join(axis for axis in cls.AXES if axis in axes.upper())

    def getAxes(self, channel):
        return self.axes[channel]

    def getSkipped(self, channel):
        """The axes left out, lower case - the form Maya's skip flags take."""
        return [axis.lower() for axis in self.AXES if axis not in self.axes[channel]]

    def isEnabled(self, channel, axis):
        return axis.upper() in self.axes[channel]

    def setEnabled(self, channel, axis, value):
        current = self.axes[channel].replace(axis.upper(), "")
        self.axes[channel] = self.cleanAxes(current + axis.upper() if value else current)

    def isFull(self):
        return all(axes == self.AXES for axes in self.axes.values())

    def serialize(self):
        return dict(self.axes)

    @classmethod
    def deserialize(cls, data):
        if not data:
            return cls()
        return cls(**{channel: data.get(channel, cls.AXES) for channel in cls.CHANNELS})

    def __str__(self):
        return "ConstraintChannels(t=%s, r=%s, s=%s)" % (
            self.axes["translate"], self.axes["rotate"], self.axes["scale"])

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
