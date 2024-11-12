from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge import NodeEditor_QGraphicEdge #type: ignore

CLASS_DEBUG = False

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2


class NodeEditorEdge(Serializable):
    def __init__(self, scene, start_socket, end_socket, edge_type = EDGE_TYPE_DIRECT):
        super().__init__()

        self.scene = scene
        self.start_socket = start_socket
        self.end_socket = end_socket

        self.start_socket.addEdge(self)
        if self.end_socket is not None:
            self.end_socket.addEdge(self)

        self.edge_type = edge_type

        self.grEdge = NodeEditor_QGraphicEdge(self)
        self.updatePositions()
        self.scene.grScene.addItem(self.grEdge)

    @property
    def edge_type(self): return self._edge_type
    @edge_type.setter
    def edge_type(self, value):
        self._edge_type = value

    def updatePositions(self):

        #add socket position to node position to get edge start position
        source_position = self.start_socket.getPosition()
        source_position[0] += self.start_socket.node.grNode.pos().x()
        source_position[1] += self.start_socket.node.grNode.pos().y()

        self.grEdge.setSourceSocketPosition(*source_position)

        #add socket position to node position to get edge end position
        if self.end_socket is not None:
            destination_position =self.end_socket.getPosition()
            destination_position[0] += self.end_socket.node.grNode.pos().x()
            destination_position[1] += self.end_socket.node.grNode.pos().y()

            self.grEdge.setDestinationSocketPosition(*destination_position)

        if CLASS_DEBUG: print("EDGE:: -updatePositions: sourcePositions: ", self.grEdge.source_position)
        if CLASS_DEBUG: print("EDGE:: -updatePositions: destinationPosition: ", self.grEdge.destination_position)

        self.grEdge.update()

    def removeFromSockets(self):

        self.start_socket = None
        self.end_socket = None

    def remove(self):

        self.removeFromSockets()
        self.scene.grScene.removeItem(self.grEdge)
        self.grEdge = None
        self.scene.removeEdge(self)