from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicSocket import NodeEditor_QGraphicSocket # type: ignore
from MNRB.MNRB_UI.mnrb_ui_utils import findIndexByAttribute #type: ignore
LEFT = 1
RIGHT = 2

REMOVE_DEBUG = False

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
        self.is_output = not is_input

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
        
        if REMOVE_DEBUG:
            print("SOCKET:: --removeEdge:: Edge to be Removed from Socket: ", edge, " with ID:: ", edge.id)
            print("SOCKET:: --removeEdge:: Currently Connected Edged to this Socket:: ")
            for index, _edge in enumerate(self.edges):
                print("SOCKET:: --removeEdge:: \t\t", _edge, " at Index:: ",  index, " with ID: ", _edge.id)
            print("SOCKET:: --removeEdge:: \t Index of Edge to be removed from Socket:: ", findIndexByAttribute(self.edges, edge.id))

        if edge in self.edges:
            index = findIndexByAttribute(self.edges, edge.id)
            del self.edges[index]
            #self.edges.remove(edge)
        else: 
            if REMOVE_DEBUG: print("SOCKET:: --removeEdge:: Edge ", edge, "is not found in the currently connected Edges: ")
            for edge in self.edges:
                if REMOVE_DEBUG: print("SOCKET:: --removeEdge:: \t\t", edge)

    def removeAllEdges(self):

        if REMOVE_DEBUG:
            print("SOCKET:: --removeAllEdges:: ")
            print("SOCKET:: --removeAllEdges:: Edges To Be Removed from Socket:: ", self)
            for index, edge in enumerate(self.edges):
                print("SOCKET:: --removeAllEdges:: \t", edge, "at index:: ", index)

        counter = 1
        while len(self.edges) > 0:
            if REMOVE_DEBUG: print("SOCKET:: --removeAllEdges::  Call:: ", counter)
            self.edges[0].remove()
            counter += 1
        
        if REMOVE_DEBUG: print("SOCKET:: --removeAllEdges:: All Edges of Socket: ",self, " Before Reset:: ", self.edges)
        self.edges = []
        if REMOVE_DEBUG: print("SOCKET:: --removeAllEdges:: All Edges of Socket: ",self, " After Reset:: ", self.edges)

    def setPosition(self):
        self.grSocket.setPos(*self.node.getSocketPosition(self.index, self.position))

    def setSize(self, size):
        self.grSocket.setSize(size)
    
    def hasEdge(self):
        return len(self.edges) > 0
    
    def __str__(self): return "ClassInstance::%s::  %s..%s" % (__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])