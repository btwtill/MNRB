"""Application-level constraint preferences.

Per-component the constraint technique is a property; per-constraint a call site
can override it in code. This is the third level: a global switch that forces one
particular *kind* of connection to native Maya constraints regardless of either.

It exists for deform connections specifically. A matrix network is cheaper and
keeps the channel box clean, but it is ROSE's own construction - baking a skeleton
out to another application, or handing it to something that only understands
Maya's own constraint nodes, is safer when the deform joints are driven by
parentConstraint/scaleConstraint instead.
"""

from PySide6.QtCore import QSettings #type: ignore

from MNRB.ROSE_Constraints.constraint_types import ConstraintType #type: ignore

SETTINGS_KEY = "deform_connections_native"


def getSettingsStore():
    return QSettings("tlpf", "ROSE")


def isDeformConnectionNative():
    stored = getSettingsStore().value(SETTINGS_KEY, False)

    #QSettings hands booleans back as strings on some platforms
    if isinstance(stored, str):
        return stored.lower() in ("1", "true", "yes")

    return bool(stored)


def setDeformConnectionNative(is_native):
    getSettingsStore().setValue(SETTINGS_KEY, bool(is_native))


def getDeformConstraintType(fallback = None):
    """The type a deform connection should use.

    Returns NATIVE when the global switch is on, otherwise `fallback` - which is
    None to mean "whatever the component is set to", the same convention the
    constraint class already uses.
    """
    return ConstraintType.NATIVE if isDeformConnectionNative() else fallback
