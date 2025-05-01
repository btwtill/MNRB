import os
from PySide2 import QtWidgets #type: ignore


class NodeEditorDragNodeListGroup(QtWidgets.QListWidgetItem):
    def __init__(self, name, parent = None):
        super().__init__(name, parent)