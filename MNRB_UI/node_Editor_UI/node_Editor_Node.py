from collections import OrderedDict
from PySide2.QtGui import QColor, QPen, QBrush # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicNode import NodeEditor_QGraphicNode # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicContent import NodeEditor_QGraphicContent # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket import NodeEditor_Socket #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket import LEFT, RIGHT #type: ignore



CLASS_DEBUG = False
EVENT_DEBUG = False
SERIALIZE_DEBUG = True

class NodeEditorNode(Serializable):
    def __init__(self, scene, title="No Title", inputs=[], outputs=[]) -> None:
        super().__init__()

        self.scene = scene

        self._title = title
        
        self.inputs = inputs
        self.outputs = outputs

        self.content = NodeEditor_QGraphicContent(self)
        self.grNode = NodeEditor_QGraphicNode(self)

        self.initSocketSettings()
        self.initSockets(inputs, outputs)

        self.scene.addNode(self)

        if CLASS_DEBUG: print("NODEEDITORNODE:: -__init__:: self.scene", self.scene)
        if CLASS_DEBUG: print("NODEEDITORNODE:: -__init__:: self.scene.grScene", self.scene.grScene)
        if CLASS_DEBUG: print("NODEEDITORNODE:: -__init__:: self.grNode", self.grNode)

        self.scene.grScene.addItem(self.grNode)

    @property
    def position(self): return self.grNode.pos()

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = self._title

    def initSocketSettings(self):
        self.input_socket_position = LEFT
        self.output_socket_position = RIGHT
        self.input_multi_edged = False
        self.output_multi_edged = True

    def initSockets(self, inputs, outputs):
        inputSockets = []
        outputSockets = []

        if CLASS_DEBUG: print("NODE:: -initSockets:: inputs: ", inputs)
        if CLASS_DEBUG: print("NODE:: -initSockets:: outputs: ", outputs)

        if CLASS_DEBUG: print("NODE:: -initSockets:: input Array Before:: ", self.inputs)
        if CLASS_DEBUG: print("NODE:: -initSockets:: output Array Befroe:: ", self.outputs)

        index_counter = 0
        on_drawn_side_counter = 0
        for input in inputs:
            if CLASS_DEBUG: print("NODE:: --initSockets:: Initilizing Input Sockets!")
            socket = NodeEditor_Socket(self, index=index_counter, 
                                       position=1, 
                                       socket_type = input[1], 
                                       socket_value = input[0],
                                       accept_multi_edges=True, 
                                       index_on_drawn_node_Side=on_drawn_side_counter, 
                                       is_input = True)
            
            index_counter += 1
            on_drawn_side_counter += 1
            inputSockets.append(socket)

        on_drawn_side_counter = 0
        for output in outputs:
            if CLASS_DEBUG: print("NODE:: --initSockets:: Initilizing output Sockets!")
            socket = NodeEditor_Socket(self, index=index_counter, 
                                        position=2,
                                        socket_type = output[1], 
                                        socket_value = output[0],
                                        accept_multi_edges =True, 
                                        index_on_drawn_node_Side = on_drawn_side_counter, 
                                        is_input = False)

            index_counter += 1
            on_drawn_side_counter += 1
            outputSockets.append(socket)

        self.inputs = inputSockets
        self.outputs = outputSockets

        if CLASS_DEBUG: print("NODE:: -initSockets:: input Array After:: ", self.inputs)
        if CLASS_DEBUG: print("NODE:: -initSockets:: output Array After:: ", self.outputs)

    def updateConnectedEdges(self):
        for socket in (self.inputs + self.outputs):
            for edge in socket.edges:
                edge.updatePositions()

    def setPosition(self, x, y):
        self.grNode.setPos(x, y)

    def getSocketPosition(self, index, position):

        if EVENT_DEBUG : print("NODE:: -getSocketPosition:: Calculating positions for Socket at Index: ", index, " Position: ", position)

        total_amount_sockets = len(self.inputs) + len(self.outputs)

        x = 0 if position == LEFT else self.grNode.width

        socket_area_distance = self.grNode.height - self.grNode.title_height - self.grNode.socket_padding
        socket_distance = socket_area_distance / total_amount_sockets

        y = self.grNode.title_height + (socket_distance * index) + self.grNode.socket_padding

        if EVENT_DEBUG : print("NODE:: -getSocketPosition:: X Position of Socket: ", x)
        if EVENT_DEBUG : print("NODE:: -getSocketPosition:: Y Position of Socket: ", y)
        
        return [x, y]
    
    def remove(self):
        if CLASS_DEBUG: print("NODE:: -remove:: Start Removing Node:: ", self)
        if CLASS_DEBUG: print("NODE:: -remove:: Removing all Edges from Sockets")
        for socket in (self.inputs + self.outputs):
            if CLASS_DEBUG: print("NODE:: -remove:: Start to Remove Edges from::", socket)
            if socket.hasEdge():
                if CLASS_DEBUG: 
                    print("NODE:: -remove:: Edges to be Removed::")
                    for edge in socket.edges:
                        print("NODE:: -remove:: \t\t ", edge)
                socket.removeAllEdges()
            else:
                if CLASS_DEBUG: print("NODE:: -remove:: \t\t None")

        if CLASS_DEBUG: print("NODE:: -remove:: Remove GrNode from the Scene")
        self.scene.grScene.removeItem(self.grNode)
        if CLASS_DEBUG: print("NODE:: -remove:: Remove Node from the Scene")
        self.scene.removeNode(self)
        if CLASS_DEBUG: print("NODE:: -remove:: Finished Removing Node ", self)

    def serialize(self):

        inputs, outputs = [], []

        for socket in self.inputs: inputs.append(socket.serialize())
        for socket in self.outputs: outputs.append(socket.serialize())

        serialized_data = OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ("position_x", self.grNode.scenePos().x()),
            ("position_y", self.grNode.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs)
        ])

        if SERIALIZE_DEBUG: print("NODE: --serialize:: Serialized Node:: ", self, " to Data:: ", serialized_data)

        return serialized_data
    
    def deserialize(self, data, hashmap = {}, restore_id = True):

        if restore_id: self.id = data['id']
        hashmap[data['id']] = self

        self.title = data['title']

        return False

    def __str__(self): return "ClassInstance::%s::  %s..%s" % (__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])