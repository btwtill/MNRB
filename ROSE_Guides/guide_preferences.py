"""Application-level guide display preferences.

Guide *size* is a per-component property. The connector mesh drawn between two
guides follows it: its thickness is the component's guide size times the factor
kept here, so resizing a component's guides resizes its connectors with them.

It used to be a fraction of the distance between the two guides, with an
optional fixed override - which made far-apart guides draw a slab, near ones a
hairline, and ignored the guide size slider entirely.
"""

from PySide6.QtCore import QSettings #type: ignore

#a new key rather than the old multiplier's: that value was a fraction of the
#guide distance and means something else entirely as a fraction of guide size
FACTOR_KEY = "guide_connector_thickness_factor"

#half the guide's radius: clearly thinner than the guide, still easy to see
DEFAULT_FACTOR = 0.5


def getSettingsStore():
    return QSettings("tlpf", "ROSE")


def readFloat(key, default_value):
    stored = getSettingsStore().value(key, default_value)
    try:
        return float(stored)
    except (TypeError, ValueError):
        return default_value


def getConnectorThicknessFactor():
    """Connector thickness as a multiple of the guide size."""
    return readFloat(FACTOR_KEY, DEFAULT_FACTOR)


def setConnectorThicknessFactor(value):
    getSettingsStore().setValue(FACTOR_KEY, float(value))
