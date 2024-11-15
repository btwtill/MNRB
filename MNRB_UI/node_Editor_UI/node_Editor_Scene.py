import json
from collections import OrderedDict
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicScene import NodeEditor_QGraphicScene # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge import NodeEditorEdge #type: ignore
from MNRB.MNRB_UI.mnrb_ui_utils import findIndexByAttribute #type: ignore

CLASS_DEBUG = False
SERIALIZE_DEBUG = True

class NodeEditorScene(Serializable):
    def __init__(self):
        super().__init__()
        
        self.grScene = NodeEditor_QGraphicScene(self)
        
        self.nodes = []
        self.edges = []
        
        self.initUI()

        if CLASS_DEBUG : print("NODE_EDITOR_SCENE:: -__init__:: Initialized Node Editor SCENE")

    def initUI(self):
    
        self.grScene_width = 64000
        self.grScene_height = 64000

        self.grScene.setGrSceneSize(self.grScene_width, self.grScene_height)

    def addNode(self, node):
        self.nodes.append(node)
    
    def addEdge(self, edge):
        self.edges.append(edge)
    
    def removeNode(self, node):
        if CLASS_DEBUG: 
            print("NODE_EDITOR_SCENE:: -removeNode:: Before:: Nodes:: ")
            print("NODE_EDITOR_SCENE:: -removeNode:: \t\t Amount", len(self.nodes))
            for index, _node in enumerate(self.nodes):
                print("NODE_EDITOR_SCENE:: -removeNode:: \t\t", _node, " at Index:: ", index, " with ID: ", _node.id)
            print("NODE_EDITOR_SCENE:: -removeNode:: Index of node to be Removed:: ", findIndexByAttribute(self.nodes, node.id))
        
        index_node_remove = findIndexByAttribute(self.nodes, node.id)
        #self.nodes.remove(node)
        del self.nodes[index_node_remove]

        if CLASS_DEBUG: 
            print("NODE_EDITOR_SCENE:: -removeNode:: After:: After:: ")
            print("NODE_EDITOR_SCENE:: -removeNode:: \t\t Amount", len(self.nodes))
            for index, _node in enumerate(self.nodes):
                print("NODE_EDITOR_SCENE:: -removeNode:: \t\t", _node, " at Index:: ", index, " with ID: ", _node.id)
    
    def removeEdge(self, edge):
        if CLASS_DEBUG: 
            print("NODE_EDITOR_SCENE:: -removeEdge:: Before:: Edges:: ")
            print("NODE_EDITOR_SCENE:: -removeEdge:: \t\t Amount", len(self.edges))
            for index, _edge in enumerate(self.edges):
                print("NODE_EDITOR_SCENE:: -removeEdge:: \t\t", _edge, " at Index:: ", index, " with ID: ", _edge.id)
            print("NODE_EDITOR_SCENE:: -removeNode:: Index of edge to be Removed:: ", findIndexByAttribute(self.edges, edge.id))

        index_edge_remove = findIndexByAttribute(self.edges, edge.id)
        #self.edges.remove(edge)
        del self.edges[index_edge_remove]

        if CLASS_DEBUG:
            print("NODE_EDITOR_SCENE:: -removeEdge:: After:: Edges:: ")
            print("NODE_EDITOR_SCENE:: -removeEdge:: \t\t Amount", len(self.edges))
            for index, _edge in enumerate(self.edges):
                print("NODE_EDITOR_SCENE:: -removeEdge:: \t\t", _edge , " at Index:: ", index, " with ID: ", _edge.id)

    def saveSceneToFile(self, filename):

        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))

        if SERIALIZE_DEBUG: print("SCENE: --saveSceneToFile:: Successfully stored Scene ", self, " to File: ", filename)

    def loadSceneFromFile(self, filename):

        with open(filename, "r") as file:
            raw_data = file.read()
            data = json.loads(raw_data)
            self.deserialize(data)
        if SERIALIZE_DEBUG: print("SCENE: --loadSceneFromFile:: Successfully loaded Scene ", self, " from File: ", filename)

    def serialize(self):
        
        nodes, edges = [] , []

        for node in self.nodes : nodes.append(node.serialize())
        for edge in self.edges : edges.append(edge.serialize())

        serialized_data = OrderedDict([
            ('id', self.id), 
            ('grScene_width', self.grScene_width), 
            ('grScene_height', self.grScene_height),
            ('nodes', nodes),
            ('edges', edges),
            ])

        if SERIALIZE_DEBUG: print("SCENE: --serialize:: Serialized Scene:: ", self, " to Data:: ", serialized_data)

        return serialized_data

    def clearScene(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()

    def deserialize(self, data, hashmap={}, restore_id = True):

        hashmap = {}

        if restore_id: self.id = data['id']

        all_current_nodes_in_scene = self.nodes.copy()

        if SERIALIZE_DEBUG:
            print("_______________________________________________________________")
            print("SCENE: --deserialize:: Starting to Deserialize Data:: ", data)

        for node_data in data['nodes']:
            found = None
            for node in all_current_nodes_in_scene:
                if node.id == node_data['id']:
                    if SERIALIZE_DEBUG: print("SCENE: --deserialize:: Found Existing node", node, " with ID: ", node.id, " matching data ID: ", node_data['id'])
                    found = node
                    break
            if not found:
                if SERIALIZE_DEBUG: 
                    print("SCENE: --deserialize:: Did not find existing node matching ID:: ", node_data['id'])
                    print("SCENE: --deserialize:: Creating New Node:: ")
                new_node = NodeEditorNode(self)
                if SERIALIZE_DEBUG: print("SCENE: --deserialize:: Done Creating New Node:: ", new_node)
                if SERIALIZE_DEBUG: print("SCENE: --deserialize:: deserializing new Node:: ", new_node)
                new_node.deserialize(node_data, hashmap, restore_id)
            else:
                if SERIALIZE_DEBUG: print("SCENE:: --deserialize:: Deserializing Existing Node:: ", found, ":: with Data:: ", node_data)
                found.deserialize(node_data, hashmap, restore_id, exists = True)
                index_to_remove = findIndexByAttribute(all_current_nodes_in_scene, found.id)
                del all_current_nodes_in_scene[index_to_remove]

        while all_current_nodes_in_scene != []:
            node = all_current_nodes_in_scene.pop()
            node.remove()

        all_current_edges_in_scene = self.edges.copy()

        for edge_data in data['edges']:
            found = None
            for edge in all_current_edges_in_scene:
                if edge.id == edge_data['id']:
                    found = edge
                    break
            if not found:
                new_edge = NodeEditorEdge(self)
                new_edge.deserialize(edge_data, hashmap, restore_id)
            else:
                found.deserialize(edge_data, hashmap, restore_id)
                index_to_remove = findIndexByAttribute(all_current_edges_in_scene, found.id)
                del all_current_edges_in_scene[index_to_remove]

        while all_current_edges_in_scene != []:
            edge = all_current_edges_in_scene.pop()
            edge.remove()

        if SERIALIZE_DEBUG: print("_______________________________________________________________SCENE DESERIALIZED")

        return True