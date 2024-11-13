from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicSocket import NodeEditor_QGraphicSocket # type: ignore

LEFT = 1
RIGHT = 2

class NodeEditor_Socket(Serializable):
    def __init__(self, node, index=0, position=LEFT, socket_type=0, socket_value ="undefined", accept_multi_edges=True, index_on_drawn_node_Side = 1, is_input = True ):
        super().__init__()

        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type
        self.socket_value = socket_value
        self.accept_multi_edges = accept_multi_edges
        self.index_on_drawn_node_Side = index_on_drawn_node_Side
        self.is_input = is_input

        self.grSocket = NodeEditor_QGraphicSocket(self)

        self.edges = []

        self.setPosition()
        self.setContentLabel()

    def getPosition(self):
        return self.node.getSocketPosition(self.index, self.position)

    def setContentLabel(self):
        self.node.content.addSocketLabel(self.socket_value, self.position, 0)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeEdge(self, edge):
        if edge in self.edges: self.edges.remove(edge)
        else: 
            print("SOCKET:: --removeEdge:: Edge ", edge, "is not found in the currently connected Edges: ")
            for edge in self.edges:
                print("SOCKET:: --removeEdge:: \t\t", edge)

    def removeAllEdges(self):
        while(self.edges):
            edge = self.edges.pop(0)
            edge.remove()

    def setPosition(self):
        self.grSocket.setPos(*self.node.getSocketPosition(self.index, self.position))

    def setSize(self, size):
        self.grSocket.setSize(size)
    
    def hasEdge(self):
        return len(self.edges) > 0
    
    def __str__(self): return "ClassInstance::%s::  %s..%s" % (__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])