from collections import OrderedDict
from PySide2.QtGui import QColor, QPen, QBrush # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicNode import NodeEditor_QGraphicNode # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicContent import NodeEditor_QGraphicContent # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket import NodeEditor_Socket #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket import LEFT, RIGHT #type: ignore

CLASS_DEBUG = False
EVENT_DEBUG = False
SERIALIZE_DEBUG = False

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
                                       accept_multi_edges=input[2], 
                                       index_on_drawn_node_side=on_drawn_side_counter, 
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
            if SERIALIZE_DEBUG: print("NODE: --deserialize:: Serialized Node:: Adding Input Data to input and output Socket Lists")
            for input in data['inputs']:
                self.inputs.append(input)

            for output in data['outputs']:
                self.outputs.append(output)
            if SERIALIZE_DEBUG: print("NODE: --deserialize:: Serialized Node:: Wrapping GrNode around the Fake sockets.")
            self.grNode.wrapGrNodeToSockets()

        for index, socket_data in enumerate(data['inputs']):
            if not exists:
                if SERIALIZE_DEBUG: print("NODE: --deserialize:: Creating new Input Socket Since there was no node found previously in the scene.")
                new_socket = NodeEditor_Socket(
                                                                        node=self, index=socket_data['index'], 
                                                                        index_on_drawn_node_side = socket_data['index_on_drawn_node_side'],
                                                                        socket_type = socket_data['socket_type'],
                                                                        socket_value = socket_data['socket_value'], 
                                                                        position = socket_data['position'],
                                                                        accept_multi_edges = socket_data['accept_multi_edges'],
                                                                        is_input = socket_data['is_input']
                                                                    )
                if SERIALIZE_DEBUG: print("NODE: --deserialize:: Created New Input Socket:: ", new_socket, " now Deserializing::")
                new_socket.deserialize(socket_data, hashmap, restore_id)
                if SERIALIZE_DEBUG: print("NODE: --deserialize:: Adding new created Node to the Input Sockets")
                self.inputs[index] = new_socket
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
                if SERIALIZE_DEBUG: print("NODE: --deserialize:: Creating new Output Socket Since there was no node found previously in the scene.")
                new_socket = NodeEditor_Socket(
                                                                        node=self, index=socket_data['index'], 
                                                                        index_on_drawn_node_side = socket_data['index_on_drawn_node_side'],
                                                                        socket_type = socket_data['socket_type'],
                                                                        socket_value = socket_data['socket_value'], 
                                                                        position = socket_data['position'],
                                                                        accept_multi_edges = socket_data['accept_multi_edges'],
                                                                        is_input = socket_data['is_input']
                                                                    )
                new_socket.deserialize(socket_data, hashmap, restore_id)
                if SERIALIZE_DEBUG: print("NODE: --deserialize:: Adding new created Node to the Output Sockets")
                self.outputs[index] = new_socket
            else:
                for socket in self.outputs:
                    if socket.id == socket_data['id']:
                        if SERIALIZE_DEBUG: print("NODE: --deserialize:: There was an Output Socket detected:: ", socket, " with ID:: ", socket.id," matching the serialized Data ID:: ", socket_data['id'])
                        found = socket
                        break
                if SERIALIZE_DEBUG: print("NODE: --deserialize:: Deserializing Found Socket:: ", found)
                found.deserialize(socket_data, hashmap, restore_id)

        if SERIALIZE_DEBUG: print("______________________________________ NODE DESERIALIZED")

        return True

    def __str__(self): return "ClassInstance::%s::  %s..%s" % (__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])