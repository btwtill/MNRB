from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGrpahicNode import NodeEditor_QGraphicNode # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicContent import NodeEditor_QGraphicContent # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket import NodeEditor_Socket #type: ignore
from PySide2.QtGui import QColor, QPen, QBrush # type: ignore


CLASS_DEBUG = True

class NodeEditorNode(Serializable):
    def __init__(self, scene, title="No Title", inputs=[], outputs=[]) -> None:
        super().__init__()

        self.scene = scene
        self.title = title
        
        self.initSockets(inputs, outputs)

        self.content = NodeEditor_QGraphicContent(self)
        self.grNode = NodeEditor_QGraphicNode(self)

        self.scene.addNode(self)

        if CLASS_DEBUG: print("NODEEDITORNODE:: -__init__:: self.scene", self.scene)
        if CLASS_DEBUG: print("NODEEDITORNODE:: -__init__:: self.scene.grScene", self.scene.grScene)
        if CLASS_DEBUG: print("NODEEDITORNODE:: -__init__:: self.grNode", self.grNode)

        self.scene.grScene.addItem(self.grNode)

    def initSockets(self, inputs, outputs):
            self.inputs = []
            self.outputs = []

            counter = 0
            for input in inputs:
                if CLASS_DEBUG: print("NODE:: --initSockets:: Initilizing Input Sockets!")
                socket = NodeEditor_Socket()

                counter += 1
                self.inputs.append(socket)

            counter = 0
            for output in outputs:
                if CLASS_DEBUG: print("NODE:: --initSockets:: Initilizing output Sockets!")
                socket = NodeEditor_Socket()

                counter += 1
                self.outputs.append(socket)

    