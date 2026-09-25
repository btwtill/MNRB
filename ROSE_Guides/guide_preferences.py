"""Application-level guide display preferences.

Guide *size* is already a per-component property. This is the connector mesh that
is drawn between two guides, whose thickness was a hardcoded tenth of the distance
between them - fine until a component has guides far enough apart that the
connector reads as a slab, or close enough that it disappears.
"""

from PySide6.QtCore import QSettings #type: ignore

MULTIPLIER_KEY = "guide_connector_thickness_multiplier"
OVERRIDE_KEY = "guide_connector_thickness_override"

#what the connector thickness was fixed at before this was configurable
DEFAULT_MULTIPLIER = 0.1
#0 means "no override" - fall back to the distance-based multiplier
DEFAULT_OVERRIDE = 0.0


def getSettingsStore():
    return QSettings("tlpf", "ROSE")


def readFloat(key, default_value):
    stored = getSettingsStore().value(key, default_value)
    try:
        return float(stored)
    except (TypeError, ValueError):
        return default_value


def getConnectorThicknessMultiplier():
    return readFloat(MULTIPLIER_KEY, DEFAULT_MULTIPLIER)


def setConnectorThicknessMultiplier(value):
    getSettingsStore().setValue(MULTIPLIER_KEY, float(value))


def getConnectorThicknessOverride():
    """A fixed thickness in world units, or 0 to keep it distance-relative."""
    return readFloat(OVERRIDE_KEY, DEFAULT_OVERRIDE)


def setConnectorThicknessOverride(value):
    getSettingsStore().setValue(OVERRIDE_KEY, float(value))
