from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGrpahicNode import NodeEditor_QGraphicNode # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicContent import NodeEditor_QGraphicContent # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket import NodeEditor_Socket #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket import LEFT, RIGHT #type: ignore
from PySide2.QtGui import QColor, QPen, QBrush # type: ignore


CLASS_DEBUG = False

class NodeEditorNode(Serializable):
    def __init__(self, scene, title="No Title", inputs=[], outputs=[]) -> None:
        super().__init__()

        self.scene = scene
        self.title = title
        
        self.inputs = inputs
        self.outputs = outputs

        self.initSocketSettings()
        self.content = NodeEditor_QGraphicContent(self)
        self.grNode = NodeEditor_QGraphicNode(self)
        self.grNode.wrapGrNodeToSockets()

        self.initSockets(inputs, outputs)

        self.scene.addNode(self)

        if CLASS_DEBUG: print("NODEEDITORNODE:: -__init__:: self.scene", self.scene)
        if CLASS_DEBUG: print("NODEEDITORNODE:: -__init__:: self.scene.grScene", self.scene.grScene)
        if CLASS_DEBUG: print("NODEEDITORNODE:: -__init__:: self.grNode", self.grNode)

        self.scene.grScene.addItem(self.grNode)

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
                                       socket_type = 0, 
                                       accept_multi_edges=False, 
                                       index_on_drawn_node_Side=on_drawn_side_counter, 
                                       is_input = True)
            
            index_counter += 1
            on_drawn_side_counter += 1
            inputSockets.append(socket)

        on_drawn_side_counter = 0
        for output in outputs:
            if CLASS_DEBUG: print("NODE:: --initSockets:: Initilizing output Sockets!")
            socket = NodeEditor_Socket(self, index=index_counter, 
                                       position=2, socket_type = 0, 
                                       accept_multi_edges=True, 
                                       index_on_drawn_node_Side=on_drawn_side_counter, 
                                       is_input = False)

            index_counter += 1
            on_drawn_side_counter += 1
            outputSockets.append(socket)

        self.inputs = inputSockets
        self.outputs = outputSockets

        if CLASS_DEBUG: print("NODE:: -initSockets:: input Array After:: ", self.inputs)
        if CLASS_DEBUG: print("NODE:: -initSockets:: output Array After:: ", self.outputs)

    def getSocketPosition(self, index, position):

        if CLASS_DEBUG : print("NODE:: -getSocketPosition:: Calculating positions for Socket at Index: ", index, " Position: ", position)

        total_amount_sockets = len(self.inputs) + len(self.outputs)

        x = 0 if position == LEFT else self.grNode.width

        socket_area_distance = self.grNode.height - self.grNode.title_height
        if CLASS_DEBUG : print("NODE:: -getSocketPosition:: totalAmoun of Sockets: ", total_amount_sockets)
        if CLASS_DEBUG : print("NODE:: -getSocketPosition:: socket Area Height: ", socket_area_distance)

        socket_distance = socket_area_distance / total_amount_sockets

        if CLASS_DEBUG : print("NODE:: -getSocketPosition:: socket Area Height: ", socket_area_distance)

        y = self.grNode.title_height + (socket_distance * index) + self.grNode.socket_padding

        if CLASS_DEBUG : print("NODE:: -getSocketPosition:: X Position of Socket: ", x)
        if CLASS_DEBUG : print("NODE:: -getSocketPosition:: Y Position of Socket: ", y)
        

        return [x, y]