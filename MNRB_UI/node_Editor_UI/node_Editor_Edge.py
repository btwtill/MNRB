from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge import NodeEditor_QGraphicEdge #type: ignore

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2


class NodeEditorEdge(Serializable):
    def __init__(self, scene, start_socket, end_socket, edge_type = EDGE_TYPE_DIRECT):
        super().__init__()

        self.scene = scene
        self.start_socket = start_socket
        self.end_socket = end_socket

        self._edge_type = edge_type

        self.grEdge = NodeEditor_QGraphicEdge(self)
        self.scene.grScene.addItem(self.grEdge)