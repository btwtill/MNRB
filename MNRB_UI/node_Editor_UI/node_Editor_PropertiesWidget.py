from PySide2 import QtWidgets #type: ignore
from PySide2.QtCore import QSize  #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore

EVENT_DEBUG = True

class NodeEditorPropertiesWidget(QtWidgets.QWidget, Serializable):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._title = "undefined"

        self.initUI()

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addStretch()
        self.setLayout(self.layout)

    def serialize(self):
        return True
    
    def deserialize(self, data, hashmap = {}, restore_id=True):
        return False