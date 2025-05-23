import json
import os
from collections import OrderedDict
from PySide2.QtCore import QRectF #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicScene import NodeEditor_QGraphicScene # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge import NodeEditorEdge #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_SceneHistory import NodeEditorSceneHistory #type: ignore
from MNRB.MNRB_UI.mnrb_ui_utils import findIndexByAttribute #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Clipboard import NodeEditorSceneClipboard #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_SceneProperties import NodeEditorSceneProperties #type: ignore
from MNRB.MNRB_UI.node_Editor_Exceptions.node_Editor_FileException import InvalidFile #type: ignore
from MNRB.MNRB_Scene.virtual_hierarchy import MNRB_Virtual_Hierarchy #type: ignore
from MNRB.MNRB_Colors.colors import MNRBSceneColors #type: ignore

CLASS_DEBUG = False
SERIALIZE_DEBUG = False
SELECTION_DEBUG = False
BUILD_DEBUG = False

class NodeEditorScene(Serializable):
    def __init__(self):
        super().__init__()
        
        self.grScene = NodeEditor_QGraphicScene(self)
        self.properties = NodeEditorSceneProperties(self)
        self.virtual_rig_hierarchy = MNRB_Virtual_Hierarchy(self)

        self.colors = MNRBSceneColors(self)

        self.nodes = []
        self.edges = []
        
        self.initUI()

        self._deformer_dict = {}

        self._last_selected_items = []

        self._has_been_modified = False
        self._has_been_modified_listeners = []
        self._scene_changed_listeners = []

        self._item_selected_listeners = []
        self._items_deselected_listeners = []

        self._build_has_been_triggered_listeners = []

        self.nodeClassSelectorFunction = None

        self.history = NodeEditorSceneHistory(self)
        self.clipboard = NodeEditorSceneClipboard(self)

        self.grScene.itemSelected.connect(self.onItemSelected)
        self.grScene.itemsDeselected.connect(self.onItemsDeselected)

        self.history.connectHistoryModifiedListenersCallback(self.properties.validateProperties)

        if CLASS_DEBUG : print("NODE_EDITOR_SCENE:: -__init__:: Initialized Node Editor SCENE")

    @property
    def has_been_modified(self): return self._has_been_modified
    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            self._has_been_modified = value

            for callback in self._has_been_modified_listeners: callback()
    
        self._has_been_modified = value
        for callback in self._scene_changed_listeners: callback()

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

    def connectViewDragEnterListenerCallback(self, callback):
        self.getView().connectViewDragEnterListenerCallback(callback)
    
    def connectViewDropListenerCallback(self, callback):
        self.getView().connectViewDropListenerCallback(callback)

    def connectSceneChangedCallback(self, callback):
        self._scene_changed_listeners.append(callback)

    def connectBuildHasBeenTriggeredListenerCallback(self, callback):
        self._build_has_been_triggered_listeners.append(callback)

    def alignSelectedNodesOnX(self):
        selected_nodes = self.getSelectedNodes()

        combined_bounding_rectangle = QRectF()
        total_height = 0

        for gr_node in selected_nodes:
            combined_bounding_rectangle = combined_bounding_rectangle.united(gr_node.mapToScene(gr_node.boundingRect()).boundingRect())
            total_height += gr_node.height + 20

        x = combined_bounding_rectangle.left()
        y = combined_bounding_rectangle.top()

        for index, gr_node in enumerate(selected_nodes):
            gr_node.node.setPosition(x, y + (total_height / len(selected_nodes)) * index)

    def alignSelectedNodesOnY(self):
        selected_nodes = self.getSelectedNodes()

        combined_bounding_rectangle = QRectF()
        total_width = 0

        for gr_node in selected_nodes:
            combined_bounding_rectangle = combined_bounding_rectangle.united(gr_node.mapToScene(gr_node.boundingRect()).boundingRect())
            total_width += gr_node.width + 20

        y = combined_bounding_rectangle.top()
        x = combined_bounding_rectangle.left()

        for index, gr_node in enumerate(selected_nodes):
            gr_node.node.setPosition(x + (total_width / len(selected_nodes)) * index, y)

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

    def getItemAt(self, pos):
        scene_pos = self.getView().mapToScene(pos)
        return self.getView().itemAt(pos.x(), pos.y())

    def getSelectedItems(self):
        return self.grScene.selectedItems()

    def getSelectedNodes(self):
        nodes = []
        for item in self.getSelectedItems():
            if hasattr(item, 'node'):
                nodes.append(item)
        return nodes

    def getNodeFromSceneByName(self, name):
        for node in self.nodes:
            if node.properties.component_name == name:
                return node

    def getView(self):
        return self.grScene.views()[0]

    def getNodeClassFromData(self, node_data):
        if self.nodeClassSelectorFunction is not None:
            return self.nodeClassSelectorFunction(node_data)
        else:
            raise ValueError("nodeClassSelectorFunction is not set.")

    def getEdgeClass(self):
        return NodeEditorEdge

    def getSceneRigName(self):
        return self.properties.getRigName()

    def getDeformerDict(self):
        deformer_list = {}

        for node in self.nodes:
            deformer_names = []
            for deform in node.deforms:
                deformer_names.append(deform.name)
            deformer_list[node.getComponentFullPrefix()] = deformer_names

        return deformer_list

    def setModified(self, state):
        self.has_been_modified = state

    def setNodeClassSelectorFunction(self, selector_function):
        self.nodeClassSelectorFunction = selector_function

    def buildSceneGuides(self):
        for node in self.nodes:
            if not node.properties.is_disabled:
                node.guideBuild()

    def buildSceneStatic(self):
        for node in self.nodes:
            if not node.properties.is_disabled:
                node.staticBuild()
        self.deformer_dict = self.getAllActiveComponentsDeformers()

    def buildSceneComponents(self):
        for node in self.nodes:
            if not node.properties.is_disabled:
                node.componentBuild()
        for callback in self._build_has_been_triggered_listeners: callback()

    def displayErrorMessage(self, message):
        self.getView().displayErrorMessage(message)

    def connectSceneComponents(self):
        for node in self.nodes:
            if not node.properties.is_disabled:
                node.componentBuild()
                
        for node in self.nodes:
            if not node.properties.is_disabled:
                node.connectComponent()

    def saveSceneToFile(self, filename):

        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
        
        self.has_been_modified = False

        if SERIALIZE_DEBUG: print("SCENE: --saveSceneToFile:: Successfully stored Scene ", self, " to File: ", filename)

    def loadSceneFromFile(self, filename):

        with open(filename, "r") as file:
            # try:
                raw_data = file.read()
                data = json.loads(raw_data)
                self.deserialize(data)
            # except json.JSONDecodeError:
            #     raise InvalidFile("%s is not a Valid Json File" % os.path.basename(filename))
            # except Exception as e:
            #     print("SCENE:: --loadSceneFromFile:: Excepting while trying to load a file to the scene:: ", e)
            
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

        properties = self.properties.serialize()

        serialized_data = OrderedDict([
            ('id', self.id), 
            ('grScene_width', self.grScene_width), 
            ('grScene_height', self.grScene_height),
            ('nodes', nodes),
            ('edges', edges),
            ('properties', properties)
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

        self.properties.deserialize(data['properties'], hashmap, restore_id)

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
                new_node = self.getNodeClassFromData(node_data)(self)
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
                new_edge = self.getEdgeClass()(self)
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