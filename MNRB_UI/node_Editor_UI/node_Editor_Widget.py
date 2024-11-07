from PySide2 import QtWidgets
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_GraphicView import NodeEditor_GraphicView
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Scene import NodeEditorScene


CLASS_DEBUG = True

class NodeEditorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        if CLASS_DEBUG : print("NODE_EDITOR_WIDGET:: -__init__:: Initialized Node Editor Widget")

        self.initUI()

        
    def initUI(self):

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout (self.layout)

        self.scene = NodeEditorScene()

        self.view = NodeEditor_GraphicView(self, self.scene.grScene)
        self.layout.addWidget(self.view)