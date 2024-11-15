from collections import OrderedDict
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge import NodeEditor_QGraphicEdge #type: ignore

CLASS_DEBUG = False
REMOVE_DEBUG = False
SERIALIZE_DEBUG = True

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2


class NodeEditorEdge(Serializable):
    def __init__(self, scene, start_socket = None, end_socket = None, edge_type = EDGE_TYPE_DIRECT):
        super().__init__()

        self.scene = scene
        self._start_socket = None
        self._end_socket = None

        self.start_socket = start_socket
        self.end_socket = end_socket

        self._edge_type = edge_type

        self.grEdge = NodeEditor_QGraphicEdge(self)
        self.scene.addEdge(self)
        self.scene.grScene.addItem(self.grEdge)

        if start_socket is not None:
            self.updatePositions()
        
    @property
    def start_socket(self): return self._start_socket
    @start_socket.setter
    def start_socket(self, value):

        if self._start_socket is not None:
            self._start_socket.removeEdge(self)

        self._start_socket = value

        if self.start_socket is not None:
            self.start_socket.addEdge(self)
    
    @property
    def end_socket(self): return self._end_socket
    @end_socket.setter
    def end_socket(self, value):

        if self._end_socket is not None:
            self._end_socket.removeEdge(self)

        self._end_socket = value

        if self.end_socket is not None:
            self.end_socket.addEdge(self)

    @property
    def edge_type(self): return self._edge_type
    @edge_type.setter
    def edge_type(self, value):

        self._edge_type = value

        self.grEdge.createEdgePathCalculator()

        if self.start_socket is not None:
            self.updatePositions()

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
        else:
            self.grEdge.setDestinationSocketPosition(*source_position)

        if CLASS_DEBUG: print("EDGE:: -updatePositions: sourcePositions: ", self.grEdge.source_position)
        if CLASS_DEBUG: print("EDGE:: -updatePositions: destinationPosition: ", self.grEdge.destination_position)

        self.grEdge.update()

    def removeFromSockets(self):

        #if REMOVE_DEBUG: print("EDGE:: --removeFromSockets:: Start Removing Edge:: ", self, "fromSockets")
        #if REMOVE_DEBUG: print("EDGE:: --removeFromSockets::  Removing from Start Socket::", self.start_socket)
        #self.start_socket.removeEdge(self)
        
        #if self.end_socket is not None:
        #   if REMOVE_DEBUG: print("EDGE:: --removeFromSockets::  Removing from End Socket::", self.end_socket)
        #  self.end_socket.removeEdge(self)

        if REMOVE_DEBUG: print("EDGE:: --removeFromSockets:: Setting Start and End Socket of Edge:: ", self, " to None")
        self.start_socket = None
        self.end_socket = None

    def remove(self):
        if REMOVE_DEBUG: print("EDGE:: --remove:: Start Removing Edge:: ", self)

        self.removeFromSockets()

        if REMOVE_DEBUG: print("EDGE:: --remove:: Removing Edge from Scene and GrScene -  Edge", self)
        self.scene.grScene.removeItem(self.grEdge)
        self.scene.removeEdge(self)
        self.grEdge = None

    def serialize(self):
        serialized_data = OrderedDict([
            ('id', self.id),
            ('edge_type', self.edge_type),
            ('start_socket', self.start_socket.id),
            ('end_socket', self.end_socket.id)
        ])

        if SERIALIZE_DEBUG: print("EDGE:: --serialize:: Serialized Edge:: ", self, " to Data:: ", serialized_data)

        return serialized_data
    
    def deserialize(self, data, hashmap = {}, restore_id = True):

        if SERIALIZE_DEBUG: print("______________________________________")
        if SERIALIZE_DEBUG: print("EDGE:: --serialize:: Start Serialized Edge:: ", self, " with Data:: ", data)
        if SERIALIZE_DEBUG: print("EDGE:: --serialize::  Hasmap for Edge:: ", hashmap)
        if self.start_socket is not None and SERIALIZE_DEBUG:
            print("EDGE:: --serialize:: previouse Start Socket id: ", self.start_socket.id, " beeing object:: ", self.start_socket)
            print("EDGE:: --serialize:: Hasmap matched start socket Id: ", data['start_socket'], " and therefore object:: ", hashmap[data['start_socket']])
        if self.end_socket is not None and SERIALIZE_DEBUG:
            print("EDGE:: --serialize:: previouse End Socket id: ", self.end_socket.id, " beeing object:: ", self.end_socket)
            print("EDGE:: --serialize:: Hasmap matched End socket Id: ", data['end_socket'], " and therefore object:: ", hashmap[data['end_socket']])

        if restore_id: self.id = data['id']
        self.start_socket = hashmap[data['start_socket']]
        self.end_socket = hashmap[data['end_socket']]
        self.edge_type = data['edge_type']

        self.updatePositions()

        if SERIALIZE_DEBUG: print("______________________________________EDGE DESERIALIZED")

        return True

    def __str__(self): return "ClassInstance::%s::  %s..%s" % (__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])