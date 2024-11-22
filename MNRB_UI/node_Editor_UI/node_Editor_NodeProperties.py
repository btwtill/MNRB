from PySide2 import QtWidgets #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_PropertiesWidget import NodeEditorPropertiesWidget #type: ignore

class NodeEditorNodeProperties(NodeEditorPropertiesWidget):
    def __init__(self, node, parent = None):
        super().__init__()

        self.node = node
        self.title = self.node.title
