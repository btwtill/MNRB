from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGrpahicNode import NodeEditor_QGraphicNode # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicContent import NodeEditor_QGraphicContent # type: ignore
from PySide2.QtGui import QColor, QPen, QBrush # type: ignore


CLASS_DEBUG = True

class NodeEditorNode(Serializable):
    def __init__(self, scene, title="No Title") -> None:
        super().__init__()

        self.scene = scene
        self.title = title
        
        self.initSockets()

        self.content = NodeEditor_QGraphicContent(self)
        self.grNode = NodeEditor_QGraphicNode(self)

        self.scene.addNode(self)

        if CLASS_DEBUG: print("NODEEDITORNODE:: -__init__:: self.scene", self.scene)
        if CLASS_DEBUG: print("NODEEDITORNODE:: -__init__:: self.scene.grScene", self.scene.grScene)
        if CLASS_DEBUG: print("NODEEDITORNODE:: -__init__:: self.grNode", self.grNode)

        self.scene.grScene.addItem(self.grNode)

    def initSockets(self):
            self.inputs = []
            self.outputs = []