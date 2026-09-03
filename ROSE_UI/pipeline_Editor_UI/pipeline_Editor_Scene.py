import json
from collections import OrderedDict
from MNRB.ROSE_Data.rose_Editor_Serializable import Serializable #type: ignore
from MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicScene import NodeEditor_QGraphicScene #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_Edge import NodeEditorEdge #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_SceneHistory import NodeEditorSceneHistory #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_Clipboard import NodeEditorSceneClipboard #type: ignore
from MNRB.ROSE_UI.rose_ui_utils import findIndexByAttribute #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_SceneProperties import PipelineEditorSceneProperties #type: ignore

CLASS_DEBUG = False
SERIALIZE_DEBUG = False
SELECTION_DEBUG = False

class PipelineEditorScene(Serializable):
    """Logical scene for the Pipeline tab's canvas - mirrors NodeEditorScene
    (node_Editor_UI/node_Editor_Scene.py) minus everything that's rig-specific
    (no virtual rig hierarchy, no guide/static/component build methods). Nodes here
    are PipelineStepNode instances that each wrap one tab's existing build method."""

    def __init__(self, node_editor_tab = None, skinning_tab = None):
        super().__init__()

        #the tabs step nodes actually call into to run their build
        self.node_editor_tab = node_editor_tab
        self.skinning_tab = skinning_tab

        self.grScene = NodeEditor_QGraphicScene(self)
        self.properties = PipelineEditorSceneProperties(self)

        self.nodes = []
        self.edges = []

        self.initUI()

        self._last_selected_items = []

        self._has_been_modified = False
        self._has_been_modified_listeners = []
        self._scene_changed_listeners = []

        self._item_selected_listeners = []
        self._items_deselected_listeners = []

        self.nodeClassSelectorFunction = None

        self.history = NodeEditorSceneHistory(self)
        self.clipboard = NodeEditorSceneClipboard(self)

        self.grScene.itemSelected.connect(self.onItemSelected)
        self.grScene.itemsDeselected.connect(self.onItemsDeselected)

        if CLASS_DEBUG: print("PIPELINE_EDITOR_SCENE:: -__init__:: Initialized Pipeline Editor Scene")

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

    def alignSelectedNodesOnX(self):
        selected_nodes = self.getSelectedNodes()
        if not selected_nodes: return

        combined_bounding_rectangle = None
        total_height = 0
        for gr_node in selected_nodes:
            rect = gr_node.mapToScene(gr_node.boundingRect()).boundingRect()
            combined_bounding_rectangle = rect if combined_bounding_rectangle is None else combined_bounding_rectangle.united(rect)
            total_height += gr_node.height + 20

        x = combined_bounding_rectangle.left()
        y = combined_bounding_rectangle.top()

        for index, gr_node in enumerate(selected_nodes):
            gr_node.node.setPosition(x, y + (total_height / len(selected_nodes)) * index)

    def alignSelectedNodesOnY(self):
        selected_nodes = self.getSelectedNodes()
        if not selected_nodes: return

        combined_bounding_rectangle = None
        total_width = 0
        for gr_node in selected_nodes:
            rect = gr_node.mapToScene(gr_node.boundingRect()).boundingRect()
            combined_bounding_rectangle = rect if combined_bounding_rectangle is None else combined_bounding_rectangle.united(rect)
            total_width += gr_node.width + 20

        y = combined_bounding_rectangle.top()
        x = combined_bounding_rectangle.left()

        for index, gr_node in enumerate(selected_nodes):
            gr_node.node.setPosition(x + (total_width / len(selected_nodes)) * index, y)

    def removeNode(self, node):
        index_node_remove = findIndexByAttribute(self.nodes, node.id)
        del self.nodes[index_node_remove]

    def removeEdge(self, edge):
        index_edge_remove = findIndexByAttribute(self.edges, edge.id)
        del self.edges[index_edge_remove]

    def onItemSelected(self):
        current_selected_items = self.getSelectedItems()
        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items
            self.history.storeHistory("Selection Changed")
            for callback in self._item_selected_listeners: callback()

    def onItemsDeselected(self):
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
        return self.getView().itemAt(pos.x(), pos.y())

    def getSelectedItems(self):
        return self.grScene.selectedItems()

    def getSelectedNodes(self):
        nodes = []
        for item in self.getSelectedItems():
            if hasattr(item, 'node'):
                nodes.append(item)
        return nodes

    def getNodeFromSceneByTitle(self, title):
        for node in self.nodes:
            if node.title == title:
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

    def setModified(self, state):
        self.has_been_modified = state

    def setNodeClassSelectorFunction(self, selector_function):
        self.nodeClassSelectorFunction = selector_function

    def displayErrorMessage(self, message):
        self.getView().displayErrorMessage(message)

    def getTopologicallySortedNodes(self):
        """Order nodes by their sequence-socket connections (input -> output).
        Falls back to appending whatever's left if a cycle/disconnected leftover
        would otherwise hang the sort - good enough for a build orchestration
        graph, not meant to be a general-purpose graph algorithm."""
        remaining = list(self.nodes)
        ordered = []

        while remaining:
            ready = [
                node for node in remaining
                if not any(
                    edge.start_socket.node in remaining
                    for input_socket in node.inputs
                    for edge in input_socket.edges
                )
            ]

            if not ready:
                ordered.extend(remaining)
                break

            for node in ready:
                ordered.append(node)
                remaining.remove(node)

        return ordered

    def buildFullPipeline(self):
        """Runs every non-disabled step in topological order. Returns a list of
        (node, success, message) - success is None for a skipped (disabled) step."""
        results = []
        for node in self.getTopologicallySortedNodes():
            if node.properties.is_disabled:
                results.append((node, None, "Skipped (disabled)"))
                continue

            success, message = node.runStep()
            results.append((node, success, message))

        return results

    def saveSceneToFile(self, filename):
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
        self.has_been_modified = False

    def loadSceneFromFile(self, filename):
        with open(filename, "r") as file:
            raw_data = file.read()
            data = json.loads(raw_data)
            self.deserialize(data)
        self.history.storeHistory("Loaded From File.", set_modified = False)

    def clearScene(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()
        self.history.storeHistory("Cleared Scene", set_modified = True)

    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())

        properties = self.properties.serialize()

        serialized_data = OrderedDict([
            ('id', self.id),
            ('grScene_width', self.grScene_width),
            ('grScene_height', self.grScene_height),
            ('nodes', nodes),
            ('edges', edges),
            ('properties', properties)
        ])
        return serialized_data

    def deserialize(self, data, hashmap={}, restore_id = True):
        hashmap = {}

        if restore_id: self.id = data['id']

        all_current_nodes_in_scene = self.nodes.copy()

        self.properties.deserialize(data['properties'], hashmap, restore_id)

        for node_data in data['nodes']:
            found = None
            for node in all_current_nodes_in_scene:
                if node.id == node_data['id']:
                    found = node
                    break
            if not found:
                new_node = self.getNodeClassFromData(node_data)(self)
                new_node.deserialize(node_data, hashmap, restore_id)
            else:
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

        return True
