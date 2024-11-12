from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicSocket import NodeEditor_QGraphicSocket # type: ignore

LEFT = 1
RIGHT = 2

class NodeEditor_Socket(Serializable):
    def __init__(self, node, index=0, position=LEFT, socket_type=0, accept_multi_edges=True, index_on_drawn_node_Side = 1, is_input = True ):
        super().__init__()

        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.accept_multi_edges = accept_multi_edges
        self.index_on_drawn_node_Side = index_on_drawn_node_Side
        self.is_input = is_input

        self.grSocket = NodeEditor_QGraphicSocket(self)

        self.edge = None

        self.setPosition()

    def getPosition(self):
        return self.node.getSocketPosition(self.index, self.position)

    def setConnectedEdge(self, edge=None):
        self.edge = edge

    def setPosition(self):
        self.grSocket.setPos(*self.node.getSocketPosition(self.index, self.position))

    def setSize(self, size):
        self.grSocket.setSize(size)