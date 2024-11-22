import json
import os
from collections import OrderedDict
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicScene import NodeEditor_QGraphicScene # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge import NodeEditorEdge #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_SceneHistory import NodeEditorSceneHistory #type: ignore
from MNRB.MNRB_UI.mnrb_ui_utils import findIndexByAttribute #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Clipboard import NodeEditorSceneClipboard #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Properties import NodeEditorProperties #type: ignore
from MNRB.MNRB_UI.node_Editor_Exceptions.node_Editor_FileException import InvalidFile #type: ignore

CLASS_DEBUG = False
SERIALIZE_DEBUG = False
SELECTION_DEBUG = True

class NodeEditorScene(Serializable):
    def __init__(self):
        super().__init__()
        
        self.grScene = NodeEditor_QGraphicScene(self)
        
        self.properties = NodeEditorProperties()
        self.properties.setTitle("Scene-Properties")
        
        self.nodes = []
        self.edges = []
        
        self.initUI()

        self._last_selected_items = []

        self._has_been_modified = False
        self._has_been_modified_listeners = []

        self._item_selected_listeners = []
        self._items_deselected_listeners = []

        self.history = NodeEditorSceneHistory(self)
        self.clipboard = NodeEditorSceneClipboard(self)

        self.grScene.itemSelected.connect(self.onItemSelected)
        self.grScene.itemsDeselected.connect(self.onItemsDeselected)

        if CLASS_DEBUG : print("NODE_EDITOR_SCENE:: -__init__:: Initialized Node Editor SCENE")

    @property
    def has_been_modified(self): return self._has_been_modified
    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            self._has_been_modified = value

            for callback in self._has_been_modified_listeners: callback()

        self._has_been_modified = value

    def initUI(self):
    
        self.grScene_width = 64000
        self.grScene_height = 64000

        self.grScene.setGrSceneSize(self.grScene_width, self.grScene_height)

    def addNode(self, node):
        self.nodes.append(node)
    
    def addEdge(self, edge):
        self.edges.append(edge)
    
    def connectHasBeenModifiedListenerCallback(self, callback):
        self._has_been_modified_listeners.append(callback)

    def connectItemSelectedListenerCallback(self, callback):
        self._item_selected_listeners.append(callback)
    
    def connectItemsDeselectedListenerCallback(self, callback):
        self._items_deselected_listeners.append(callback)

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
        del self.edges[index_edge_remove]

        if CLASS_DEBUG:
            print("NODE_EDITOR_SCENE:: -removeEdge:: After:: Edges:: ")
            print("NODE_EDITOR_SCENE:: -removeEdge:: \t\t Amount", len(self.edges))
            for index, _edge in enumerate(self.edges):
                print("NODE_EDITOR_SCENE:: -removeEdge:: \t\t", _edge , " at Index:: ", index, " with ID: ", _edge.id)

    def onItemSelected(self):
        if SELECTION_DEBUG: print("SCENE:: --onItemSelected:: Executing On Selection Callbacks ")
        current_selected_items = self.getSelectedItems()
        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items
            self.history.storeHistory("Selection Changed")
            for callback in self._item_selected_listeners: callback()

    def onItemsDeselected(self):
        if SELECTION_DEBUG: print("SCENE:: --onItemDeselect:: Executing On Deselection Selection Callbacks")
    
        current_selected_items = self.getSelectedItems()
        if self._last_selected_items == current_selected_items:
            return
        self.reset_last_selected_states()
        
        if current_selected_items == []:
            self._last_selected_items = []
            self.history.storeHistory("Deselect Everything")
            for callback in self._items_deselected_listeners: callback()

    def doDeselectItems(self, silent = False):
        for item in self.getSelectedItems():
            item.setSelected(False)

    def reset_last_selected_states(self):
        for node in self.nodes:
            node.grNode._last_selected_state = False
        for edge in self.edges:
            edge.grEdge._las_selected_state = False

    def isModified(self):
        return self.has_been_modified

    def getSelectedItems(self):
        return self.grScene.selectedItems()

    def getView(self):
        return self.grScene.views()[0]

    def saveSceneToFile(self, filename):

        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
        
        self.has_been_modified = False

        if SERIALIZE_DEBUG: print("SCENE: --saveSceneToFile:: Successfully stored Scene ", self, " to File: ", filename)

    def loadSceneFromFile(self, filename):

        with open(filename, "r") as file:
            try:
                raw_data = file.read()
                data = json.loads(raw_data)
                self.deserialize(data)
            except json.JSONDecodeError:
                raise InvalidFile("%s is not a Valid Json File" % os.path.basename(filename))
            except Exception as e:
                print("SCENE:: --loadSceneFromFile:: Excepting while trying to load a file to the scene:: ", e)
            
        if SERIALIZE_DEBUG: print("SCENE: --loadSceneFromFile:: Successfully loaded Scene ", self, " from File: ", filename)
        self.history.storeHistory("Loaded From File.", set_modified = False)

    def clearScene(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()
        
        self.history.storeHistory("Cleared Scene", set_modified = True)

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