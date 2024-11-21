from PySide2 import QtWidgets #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore

class NodeEditorProperties(QtWidgets.QWidget, Serializable):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def serialize(self):
        return True
    
    def deserialize(self, data, hashmap = {}, restore_id=True):
        return False