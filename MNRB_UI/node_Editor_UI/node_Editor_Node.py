from collections import OrderedDict
from PySide2.QtGui import QColor, QPen, QBrush # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicNode import NodeEditor_QGraphicNode # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicContent import NodeEditor_QGraphicContent # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket import NodeEditor_Socket #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket import LEFT, RIGHT #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_NodeProperties import NodeEditorNodeProperties #type: ignore

CLASS_DEBUG = False
EVENT_DEBUG = False
SERIALIZE_DEBUG = False
REMOVE_DEBUG = False

class NodeEditorNode(Serializable):

    Graphics_Node_Class = NodeEditor_QGraphicNode
    Node_Content_Class = NodeEditor_QGraphicContent
    Node_Properties_Class = NodeEditorNodeProperties
    Socket_Class = NodeEditor_Socket

    def __init__(self, scene, title="No Title", inputs=[], outputs=[]) -> None:
        super().__init__()

        self.scene = scene
        
        self._title = title
        
        self.inputs = inputs
        self.outputs = outputs

        self.content = None
        self.grNode = None
        self.properties = None

        self.initInnerClasses()
        self.initSocketSettings()
        self.initSockets(inputs, outputs)

        self.scene.addNode(self)

        if CLASS_DEBUG: print("NODEEDITORNODE:: --__init__:: self.scene", self.scene)
        if CLASS_DEBUG: print("NODEEDITORNODE:: --__init__:: self.scene.grScene", self.scene.grScene)
        if CLASS_DEBUG: print("NODEEDITORNODE:: --__init__:: self.grNode", self.grNode)

        if CLASS_DEBUG: print("NODEEDITORNODE:: --__init__:: grScene Items before adding:: ")
        if CLASS_DEBUG: 
            for item in self.scene.grScene.items():
                print("NODEEDITORNODE:: --__init__:: \t\t", item)
        self.scene.grScene.addItem(self.grNode)

        if CLASS_DEBUG: print("NODEEDITORNODE:: --__init__:: grScene Items after adding:: ")
        if CLASS_DEBUG: 
            for item in self.scene.grScene.items():
                print("NODEEDITORNODE:: --__init__:: \t\t", item)

    @property
    def position(self): return self.grNode.pos()

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = self._title
        self.properties.title = self._title

    def initInnerClasses(self):
        content_class = self.getNodeContentClass()
        graphic_node_class = self.getGraphicNodeClass()
        properties_class = self.getNodePropertiesClass()

        if CLASS_DEBUG: print("NODEEDITORNODE:: --initInnerClasses:: content Class::", content_class)
        if CLASS_DEBUG: print("NODEEDITORNODE:: --initInnerClasses:: graphicsNode Class::", graphic_node_class)
        if CLASS_DEBUG: print("NODEEDITORNODE:: --initInnerClasses:: properties_Class:: ", properties_class)

        if content_class is not None: self.content = content_class(self)
        if graphic_node_class is not None: self.grNode = graphic_node_class(self)
        if properties_class is not None: self.properties = properties_class(self)

    def initSocketSettings(self):
        self.input_socket_position = LEFT
        self.output_socket_position = RIGHT

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
            socket = self.__class__.Socket_Class(self, index=index_counter, 
                                       position=1, 
                                       socket_type = input[1], 
                                       socket_value = input[0],
                                       accept_multi_edges=input[2], 
                                       index_on_drawn_node_side=on_drawn_side_counter, 
                                       is_input = True)
            
            index_counter += 1
            on_drawn_side_counter += 1
            inputSockets.append(socket)

        on_drawn_side_counter = 0
        for output in outputs:
            if CLASS_DEBUG: print("NODE:: --initSockets:: Initilizing output Sockets!")
            socket = self.__class__.Socket_Class(self, index=index_counter, 
                                        position=2,
                                        socket_type = output[1], 
                                        socket_value = output[0],
                                        accept_multi_edges =output[2], 
                                        index_on_drawn_node_side = on_drawn_side_counter, 
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

    def getPosition(self):
        return self.grNode.pos()

    def setPosition(self, x, y):
        self.grNode.setPos(x, y)
        self.updateConnectedEdges()

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
        if REMOVE_DEBUG: print("%s:: --remove:: start Removing Node:: " % self.__class__.__name__, self)
        if REMOVE_DEBUG: print("NODE:: -remove:: Start Removing Node:: ", self)
        if REMOVE_DEBUG: print("NODE:: -remove:: Removing all Edges from Sockets")
        for socket in (self.inputs + self.outputs):
            if REMOVE_DEBUG: print("NODE:: -remove:: Start to Remove Edges from::", socket)
            if socket.hasEdge():
                if REMOVE_DEBUG: 
                    print("NODE:: -remove:: Edges to be Removed::")
                    for edge in socket.edges:
                        print("NODE:: -remove:: \t\t ", edge)
                socket.removeAllEdges()
            else:
                if REMOVE_DEBUG: print("NODE:: -remove:: \t\t None")

        if REMOVE_DEBUG: print("NODE:: -remove:: Remove GrNode from the Scene")
        self.scene.grScene.removeItem(self.grNode)
        if REMOVE_DEBUG: print("NODE:: -remove:: Remove Node from the Scene")
        self.scene.removeNode(self)
        if REMOVE_DEBUG: print("NODE:: -remove:: Finished Removing Node ", self)

    def getInputNodesFromSocket(self, index):
        input_socket = self.inputs[index]
        if len(input_socket.edges) == 0: return None
        connecting_edges = input_socket.edges
        input_nodes = []

        for edge in connecting_edges:
            other_socket = edge.getOtherSocket(input_socket)
            input_nodes.append(other_socket.node)

    def getInputSocketValue(self, index):
        input_socket = self.inputs[index]
        if len(input_socket.edges) == 0: return None
        connecting_edge = input_socket.edges[0]
        other_socket = connecting_edge.getOtherSocket(input_socket)
        socket_value = other_socket.socket_value
        return socket_value

    def getInputSocketValueWithNode(self, index):
        input_socket = self.inputs[index]
        if len(input_socket.edges) == 0: return None
        connecting_edge = input_socket.edges[0]
        other_socket = connecting_edge.getOtherSocket(input_socket)
        socket_value = other_socket.socket_value
        return socket_value, other_socket.node

    def getNodeContentClass(self):
        return self.__class__.Node_Content_Class

    def getNodeSocketClass(self):
        pass

    def getGraphicNodeClass(self):
        return self.__class__.Graphics_Node_Class

    def getNodePropertiesClass(self):
        return self.__class__.Node_Properties_Class

    def serialize(self):

        inputs, outputs = [], []

        if SERIALIZE_DEBUG: print("%s:: SERIALIZE:: Inputs:: " % self.__class__.__name__, self.inputs)
        if SERIALIZE_DEBUG: print("%s:: SERIALIZE:: Outputs:: " % self.__class__.__name__, self.outputs)

        if self.inputs != []:
            for socket in self.inputs: inputs.append(socket.serialize())
        if self.outputs != []:
            for socket in self.outputs: outputs.append(socket.serialize())

        properties = self.properties.serialize()

        serialized_data = OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ("position_x", self.grNode.scenePos().x()),
            ("position_y", self.grNode.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs),
            ('properties', properties)
        ])

        if SERIALIZE_DEBUG: print("NODE: --serialize:: Serialized Node:: ", self, " to Data:: ", serialized_data)

        return serialized_data
    
    def deserialize(self, data, hashmap = {}, restore_id = True, exists = False):
        
        if SERIALIZE_DEBUG:
            print("______________________________________")
            print("NODE: --deserialize:: Starting to Deserialize Node:: ", self, "with Data", data)
            print("NODE: --deserialize:: Setting old id: ", self.id, "to new dataID: ", data['id'])

        if restore_id: self.id = data['id']
        hashmap[data['id']] = self

        self.title = data['title']

        self.setPosition(data['position_x'], data['position_y'])

        data['inputs'].sort(key=lambda socket: socket['index_on_drawn_node_side'] + socket['position'] * 10000)
        data['outputs'].sort(key=lambda socket: socket['index_on_drawn_node_side'] + socket['position'] * 10000)

        if not exists:
            self.grNode.wrapGrNodeToSockets()

        for index, socket_data in enumerate(data['inputs']):
            if not exists:
                if SERIALIZE_DEBUG: print("NODE: --deserialize:: About to deserialize Input:: ", self.inputs[index])
                self.inputs[index].deserialize(socket_data, hashmap, restore_id)
            else:
                for socket in self.inputs:
                    if socket.id  == socket_data['id']:
                        if SERIALIZE_DEBUG: print("NODE: --deserialize:: There was an Input Socket detected:: ", socket, " with ID:: ", socket.id," matching the serialized Data ID:: ", socket_data['id'])
                        found = socket
                        break
                if SERIALIZE_DEBUG: print("NODE: --deserialize:: Deserializing Found Socket:: ", found)
                found.deserialize(socket_data, hashmap, restore_id)
        
        for index, socket_data in enumerate(data['outputs']):
            if not exists:
                if SERIALIZE_DEBUG: print("NODE: --deserialize:: About to deserialize outputs socket:: ", self.outputs[index])
                self.outputs[index].deserialize(socket_data, hashmap, restore_id)
            else:
                for socket in self.outputs:
                    if socket.id == socket_data['id']:
                        if SERIALIZE_DEBUG: print("NODE: --deserialize:: There was an Output Socket detected:: ", socket, " with ID:: ", socket.id," matching the serialized Data ID:: ", socket_data['id'])
                        found = socket
                        break
                if SERIALIZE_DEBUG: print("NODE: --deserialize:: Deserializing Found Socket:: ", found)
                found.deserialize(socket_data, hashmap, restore_id)
        
        self.properties.deserialize(data['properties'], hashmap, restore_id)

        if SERIALIZE_DEBUG: print("______________________________________ NODE DESERIALIZED")

        return True

    def __str__(self): return "ClassInstance::%s::  %s..%s" % (self.__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])