import json
from collections import OrderedDict
from MNRB.ROSE_Data.rose_Editor_Serializable import Serializable #type: ignore
from MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicScene import NodeEditor_QGraphicScene #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_Edge import NodeEditorEdge #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_SceneHistory import NodeEditorSceneHistory #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_Clipboard import NodeEditorSceneClipboard #type: ignore
from MNRB.ROSE_UI.rose_ui_utils import findIndexByAttribute #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_SceneProperties import PipelineEditorSceneProperties #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_conf import (OPERATIONCODE_ATTRIBUTE_NODE, #type: ignore
                                                                    OPERATIONCODE_CONTROL_NODE,
                                                                    OPERATIONCODE_SCENE_TARGET_NODE)
from MNRB.ROSE_Attributes.rig_root_attribute_host import RIG_ROOT_HOST_ID #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")
serialize_log = ROSE_Log.get("rose.serialize")

class AttributeEditorScene(Serializable):
    """Logical scene for the attribute canvas.

    Same shape as PipelineEditorScene - a NodeEditorScene without the rig-specific
    parts - but where a pipeline edge means "runs after", an edge here means
    "drives" or "is proxied onto", depending on what it lands on.
    """

    def __init__(self, attribute_tab = None):
        super().__init__()

        self.attribute_tab = attribute_tab

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

    def initUI(self):
        self.grScene_width = 64000
        self.grScene_height = 64000
        self.grScene.setGrSceneSize(self.grScene_width, self.grScene_height)

    def getRigScene(self):
        """The rig graph, where attributes and controls actually live."""
        if self.attribute_tab is None:
            return None
        return self.attribute_tab.getScene()

    def getCustomAttributes(self):
        if self.attribute_tab is None:
            return []
        return self.attribute_tab.rig_root_host.attributes

    def getCustomAttributeById(self, attribute_id):
        return next((custom for custom in self.getCustomAttributes()
                     if custom.id == attribute_id), None)

    def findAttributeById(self, attribute_id):
        """Look an attribute up by id across both pools - component-owned and
        rig-root. Ids are derived from (owner id, attribute name), so this is
        exact and is the only lookup a freshly dragged attribute ever needs."""
        rig_scene = self.getRigScene()
        if rig_scene is not None:
            component_attribute = rig_scene.getAttributeById(attribute_id)
            if component_attribute is not None:
                return component_attribute
        return self.getCustomAttributeById(attribute_id)

    def findAttributeByNameInOwner(self, owner_id, attribute_name):
        """Name fallback for a reference restored from a file, deliberately
        scoped to the owner it was authored against.

        Searching by name across the whole rig would hand back some other
        component's identically named attribute - every component has a
        Control_Visibility - and a rig-root attribute sharing that name would be
        silently rebound to a component.
        """
        if owner_id is None:
            return None

        if owner_id == RIG_ROOT_HOST_ID:
            return next((custom for custom in self.getCustomAttributes()
                         if custom.attribute_name == attribute_name), None)

        rig_scene = self.getRigScene()
        if rig_scene is None:
            return None

        for node in rig_scene.nodes:
            if node.id == owner_id:
                return next((candidate for candidate in node.attributes
                             if candidate.attribute_name == attribute_name), None)
        return None

# Scene plumbing, matching NodeEditorScene's contract

    @property
    def has_been_modified(self): return self._has_been_modified
    @has_been_modified.setter
    def has_been_modified(self, value):
        self._has_been_modified = value
        for callback in self._has_been_modified_listeners: callback()
        for callback in self._scene_changed_listeners: callback()

    def isModified(self): return self.has_been_modified
    def setModified(self, state): self.has_been_modified = state

    def addNode(self, node): self.nodes.append(node)
    def addEdge(self, edge): self.edges.append(edge)

    def removeNode(self, node):
        index = findIndexByAttribute(self.nodes, node.id)
        if index is not None:
            del self.nodes[index]

    def removeEdge(self, edge):
        index = findIndexByAttribute(self.edges, edge.id)
        if index is not None:
            del self.edges[index]

    def connectHasBeenModifiedListenerCallback(self, callback): self._has_been_modified_listeners.append(callback)
    def connectItemSelectedListenerCallback(self, callback): self._item_selected_listeners.append(callback)
    def connectItemsDeselectedListenerCallback(self, callback): self._items_deselected_listeners.append(callback)
    def connectSceneChangedCallback(self, callback): self._scene_changed_listeners.append(callback)

    def onItemSelected(self):
        current = self.getSelectedItems()
        if current != self._last_selected_items:
            self._last_selected_items = current
            self.history.storeHistory("Selection Changed")
            for callback in self._item_selected_listeners: callback()

    def onItemsDeselected(self):
        current = self.getSelectedItems()
        if self._last_selected_items == current:
            return
        self.reset_last_selected_states()
        if current == []:
            self._last_selected_items = []
            self.history.storeHistory("Deselect Everything")
            for callback in self._items_deselected_listeners: callback()

    def reset_last_selected_states(self):
        for node in self.nodes:
            node.grNode._last_selected_state = False
        for edge in self.edges:
            edge.grEdge._las_selected_state = False

    def doDeselectItems(self, silent = False):
        for item in self.getSelectedItems():
            item.setSelected(False)

    def getSelectedItems(self): return self.grScene.selectedItems()
    def getView(self): return self.grScene.views()[0]
    def getItemAt(self, pos): return self.getView().itemAt(pos.x(), pos.y())
    def getEdgeClass(self): return NodeEditorEdge
    def displayErrorMessage(self, message): self.getView().displayErrorMessage(message)

    def getSelectedNodes(self):
        return [item for item in self.getSelectedItems() if hasattr(item, 'node')]

    def setNodeClassSelectorFunction(self, selector_function):
        self.nodeClassSelectorFunction = selector_function

    def getNodeClassFromData(self, node_data):
        if self.nodeClassSelectorFunction is None:
            raise ValueError("nodeClassSelectorFunction is not set.")
        return self.nodeClassSelectorFunction(node_data)

    def alignSelectedNodesOnX(self): pass
    def alignSelectedNodesOnY(self): pass

    def clearScene(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()
        self.history.storeHistory("Cleared Scene", set_modified = True)

# Validation and building

    def validateAllNodes(self):
        for node in self.nodes:
            node.validate()

    def getNodesByOperationCode(self, operation_code):
        return [node for node in self.nodes if node.operation_code == operation_code]

    def build(self):
        """Realise the graph in Maya.

        Strictly ordered: every operator's Maya node is created first so that all
        plugs resolve, then attribute-driving connections, then the control
        proxies last - a proxy has to point at an attribute that already exists
        and is already wired.
        """
        self.validateAllNodes()

        messages = []
        failures = []

        operator_nodes = [node for node in self.nodes
                          if node.operation_code not in (OPERATIONCODE_ATTRIBUTE_NODE,
                                                         OPERATIONCODE_CONTROL_NODE,
                                                         OPERATIONCODE_SCENE_TARGET_NODE)]

        for node in operator_nodes:
            success, detail = node.buildNode()
            if not success:
                failures.append("%s: %s" % (node.title, detail))

        for node in operator_nodes:
            node.connectInputs()

        #attribute targets and scene-plug targets are both just "connect the
        #upstream value into me", so they run in the same pass
        for operation_code in (OPERATIONCODE_ATTRIBUTE_NODE, OPERATIONCODE_SCENE_TARGET_NODE):
            for node in self.getNodesByOperationCode(operation_code):
                success, detail = node.buildDrivingConnections()
                if not success:
                    failures.append(detail)

        proxied = 0
        for node in self.getNodesByOperationCode(OPERATIONCODE_CONTROL_NODE):
            success, detail = node.buildProxies()
            if not success:
                failures.append(detail)
            else:
                proxied += len(node.built_proxy_names)
                if detail:
                    messages.append("%s skipped %s" % (node.title, ", ".join(detail)))

        if failures:
            return False, "; ".join(failures)

        message = "Proxied %d attribute(s), built %d operator(s)" % (proxied, len(operator_nodes))
        if messages:
            message += " - " + "; ".join(messages)
        return True, message

    def removeBuiltNodes(self):
        for node in self.nodes:
            node.removeBuiltNodes()

# Serialization

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('grScene_width', self.grScene_width),
            ('grScene_height', self.grScene_height),
            ('nodes', [node.serialize() for node in self.nodes]),
            ('edges', [edge.serialize() for edge in self.edges]),
        ])

    def deserialize(self, data, hashmap = {}, restore_id = True):
        hashmap = {}
        if restore_id: self.id = data['id']

        self.clearScene()

        for node_data in data.get('nodes', []):
            new_node = self.getNodeClassFromData(node_data)(self)
            new_node.deserialize(node_data, hashmap, restore_id)

        for edge_data in data.get('edges', []):
            new_edge = self.getEdgeClass()(self)
            new_edge.deserialize(edge_data, hashmap, restore_id)

        self.validateAllNodes()
        serialize_log.debug("ATTRIBUTE_EDITOR_SCENE:: --deserialize:: restored",
                            len(self.nodes), "nodes and", len(self.edges), "edges")
        return True

    def saveSceneToFile(self, filename):
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
        self.has_been_modified = False

    def loadSceneFromFile(self, filename):
        with open(filename, "r") as file:
            self.deserialize(json.loads(file.read()))
        self.history.storeHistory("Loaded From File.", set_modified = False)
