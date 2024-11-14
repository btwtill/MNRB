from PySide2 import QtWidgets # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicView import NodeEditor_QGraphicView # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Scene import NodeEditorScene # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge import NodeEditorEdge#type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge import EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER #type: ignore

CLASS_DEBUG = False

class NodeEditorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        if CLASS_DEBUG : print("NODE_EDITOR_WIDGET:: -__init__:: Initialized Node Editor Widget")

        self.initUI()

        #debug use only remove later
        self.addTestContent()

    def initUI(self):

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout (self.layout)

        self.scene = NodeEditorScene()

        self.view = NodeEditor_QGraphicView(self.scene.grScene, self)
        self.layout.addWidget(self.view)
        self.view.centerOn(0, 0)

    def addTestContent(self):
        content_node_01 = NodeEditorNode(self.scene, title = "Node 01", inputs = [["input 01", 0]], outputs=[["output 01", 3]] )
        content_node_02 = NodeEditorNode(self.scene, title = "Node 02", inputs = [["arm_def",0],["arm_ctrl",0]], outputs=[["arm_def",1],["arm_ctrl",1]] )

        content_node_01.setPosition(-120, 20)
        content_node_02.setPosition(140, -20)

        content_edge_01 = NodeEditorEdge(self.scene, content_node_01.outputs[0], content_node_02.inputs[0], edge_type = EDGE_TYPE_BEZIER)

        content_edge_02 = NodeEditorEdge(self.scene, content_node_01.outputs[0], content_node_02.inputs[1], edge_type = EDGE_TYPE_BEZIER)

        

