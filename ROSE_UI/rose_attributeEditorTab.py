from collections import OrderedDict
import json, os
from PySide6 import QtWidgets #type: ignore
from PySide6.QtCore import Qt, QTimer #type: ignore
from MNRB.ROSE_Data.rose_Editor_Serializable import Serializable #type: ignore
from MNRB.ROSE_Attributes.rig_root_attribute_host import RigRootAttributeHost #type: ignore
from MNRB.ROSE_Attributes.attribute_types import AttributeType #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_SourceList import (AttributeEditorAttributeList, #type: ignore
                                                                          AttributeEditorControlList)
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_Widget import AttributeEditorWidget #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_Toolbar import AttributeEditorToolbar #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_conf import (OPERATIONCODE_ATTRIBUTE_NODE, #type: ignore
                                                                    OPERATIONCODE_CONTROL_NODE)
from MNRB.ROSE_UI.UI_GraphicComponents.scrollable_dock_widget import ScrollableDockWidget #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore
from MNRB.ROSE_UI.rose_ui_utils import findProjectGraphFile #type: ignore

log = ROSE_Log.get("rose.components")

class rose_AttributeEditorTab(QtWidgets.QMainWindow, Serializable):
    """Wires attributes to controls and to each other.

    A canvas rather than a list, because the relationships are a graph: one
    attribute can drive many, a driven attribute can drive further, and operators
    sit in between. Attributes and controls are dragged in from the palettes;
    operators come from the canvas's right-click menu.
    """

    def __init__(self, node_editor, parent = None):
        QtWidgets.QMainWindow.__init__(self, parent)
        Serializable.__init__(self)

        self.is_tab_widget = True
        self.node_editor = node_editor

        #attributes belonging to the rig rather than any component - hosted on the
        #rig root, which exists whether or not components do
        self.rig_root_host = RigRootAttributeHost(self.getScene())

        self._has_been_modified = False
        self._has_been_modified_listeners = []
        self._selection_changed_listeners = []

        self.initUI()

    def getScene(self):
        """The rig graph - where attributes and controls actually live."""
        return self.node_editor.central_widget.scene

    def getGraphScene(self):
        """This tab's own canvas."""
        return self.central_widget.scene

    def initUI(self):
        self.addDockWidgets()

        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self.toolbar = AttributeEditorToolbar(self)
        container_layout.addWidget(self.toolbar)

        self.central_widget = AttributeEditorWidget(self, self.properties_dock)
        container_layout.addWidget(self.central_widget)

        self.setCentralWidget(container)

        self.getGraphScene().connectHasBeenModifiedListenerCallback(self.onGraphModified)

        #deferred so the view has its real size before it centres, same reasoning
        #as the other two canvases
        QTimer.singleShot(0, self.central_widget.centerView)

    def addDockWidgets(self):
        self.attribute_dock = QtWidgets.QDockWidget("Exposed Attributes", self)
        self.attribute_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.attribute_list = AttributeEditorAttributeList(self)
        self.attribute_dock.setWidget(self.attribute_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.attribute_dock)

        self.control_dock = QtWidgets.QDockWidget("Controls", self)
        self.control_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.control_list = AttributeEditorControlList(self)
        self.control_dock.setWidget(self.control_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.control_dock)

        self.properties_dock = ScrollableDockWidget("Node Properties", self)
        self.properties_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.properties_dock.setMinimumWidth(250)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_dock)

        #properties sit under the control palette rather than beside it, so the
        #canvas keeps the width
        self.splitDockWidget(self.control_dock, self.properties_dock, Qt.Vertical)

# Modified / selection plumbing

    @property
    def has_been_modified(self):
        return self._has_been_modified
    @has_been_modified.setter
    def has_been_modified(self, value):
        self._has_been_modified = value
        for callback in self._has_been_modified_listeners:
            callback()

    def setModified(self, state): self.has_been_modified = state
    def isModified(self): return self.has_been_modified

    def onGraphModified(self):
        self.setModified(self.getGraphScene().isModified())

    def connectHasBeenModifiedListenerCallback(self, callback):
        self._has_been_modified_listeners.append(callback)

    def connectSelectionChangedListenerCallback(self, callback):
        self._selection_changed_listeners.append(callback)

    def notifySelectionChanged(self):
        for callback in self._selection_changed_listeners:
            callback()

# Palettes

    def getAttributeGroups(self):
        groups = self.getScene().getAttributeDict()

        custom_entries = [{"id": custom.id, "name": custom.attribute_name}
                          for custom in self.rig_root_host.attributes]
        if custom_entries:
            groups[str(self.rig_root_host.id)] = {"label": "Rig Root", "attributes": custom_entries}

        return groups

    def refreshSourceLists(self):
        self.attribute_list.refresh(self.getAttributeGroups())
        self.control_list.refresh(self.getScene().getControlDict())

    def activate(self):
        #the rig graph may have changed while another tab was in front
        self.refreshSourceLists()
        self.getGraphScene().validateAllNodes()
        self.updateRemoveDeprecatedButtonState()

    def addCustomAttribute(self, name, attribute_type = AttributeType.FLOAT, options = None):
        if self.rig_root_host.addAttribute(name, attribute_type, options = options) is None:
            log.warning("ATTRIBUTEEDITORTAB:: --addCustomAttribute:: '%s' already exists" % name)
            return False

        self.setModified(True)
        self.refreshSourceLists()
        return True

# Deprecated handling

    def getUnresolvedNodes(self):
        """Nodes whose attribute or control no longer exists in the rig."""
        unresolved = []
        for node in self.getGraphScene().nodes:
            if node.operation_code == OPERATIONCODE_ATTRIBUTE_NODE and node.resolveAttribute() is None:
                unresolved.append(node)
            elif node.operation_code == OPERATIONCODE_CONTROL_NODE and node.resolveControl() is None:
                unresolved.append(node)
        return unresolved

    def updateRemoveDeprecatedButtonState(self):
        self.toolbar.setRemoveDeprecatedEnabled(len(self.getUnresolvedNodes()) > 0)

    def onRemoveDeprecated(self):
        unresolved = self.getUnresolvedNodes()
        for node in unresolved:
            #removing the node takes its edges with it, so every control that was
            #proxying it drops the entry on its next sync
            node.remove()

        if unresolved:
            self.setModified(True)
            self.getGraphScene().history.storeHistory("Removed Deprecated Nodes", set_modified = True)

        self.getGraphScene().validateAllNodes()
        self.updateRemoveDeprecatedButtonState()

# Building

    def onBuildAll(self):
        self.rig_root_host.buildAttributes()
        success, message = self.getGraphScene().build()

        if success:
            log.info("ATTRIBUTEEDITORTAB:: --onBuildAll:: ", message)
        else:
            log.warning("ATTRIBUTEEDITORTAB:: --onBuildAll:: ", message)

        return success, message

    #kept so the Attributes pipeline step and the toolbar share one entry point
    def onBuildSelected(self):
        return self.onBuildAll()

# Edit menu contract

    def canCut(self): return False
    def canCopy(self): return False
    def canMirrorNode(self): return False
    def canUndo(self): return self.getGraphScene().history.canUndo()
    def canRedo(self): return self.getGraphScene().history.canRedo()
    def canDelete(self): return self.central_widget.sceneHasSelectedItems()

    def onDelete(self): self.central_widget.view.deleteSelected()
    def onUndo(self): self.getGraphScene().history.undo()
    def onRedo(self): self.getGraphScene().history.redo()

# Project file

    def onOpenFile(self, file_path):
        if os.path.isdir(file_path):
            graph_file = findProjectGraphFile(file_path)
            if graph_file is not None:
                self.loadFile(graph_file)
            else:
                self.onNewFile()
        elif os.path.isfile(file_path):
            self.loadFile(file_path)
        return True

    def loadFile(self, file_path):
        self.failed_load_path = None
        try:
            with open(file_path, "r") as file:
                self.deserialize(json.loads(file.read()))
        except Exception as e:
            #a corrupted graph file shouldn't take down the whole project open
            log.error("ATTRIBUTEEDITORTAB:: --loadFile:: could not load '%s': %s - starting empty" % (file_path, e))
            self.failed_load_path = file_path
            self.onNewFile()
            return False
        return True

    def onSaveFile(self, file_name):
        #see rose_skinningEditorTab.saveFileToPath: a load that failed quietly
        #leaves this tab empty while the real data is still on disk, and a save
        #that runs unconditionally then makes the loss permanent
        if getattr(self, "failed_load_path", None) is not None:
            log.error("ATTRIBUTEEDITORTAB:: --onSaveFile:: Not saving: '%s' could not be read earlier, so this tab is empty and "
                      "saving would overwrite the project's real data." % self.failed_load_path)
            return False

        with open(file_name, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
        self.setModified(False)
        return True

    def onNewFile(self):
        self.getGraphScene().clearScene()
        self.rig_root_host.attributes = []
        self.refreshSourceLists()
        self.setModified(False)

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('rig_root_attributes', self.rig_root_host.serialize()),
            ('graph', self.getGraphScene().serialize()),
        ])

    def deserialize(self, data, hashmap = {}, restore_id = True):
        if restore_id: self.id = data['id']

        #custom attributes first: the graph's attribute nodes resolve against them
        self.rig_root_host.deserialize(data.get('rig_root_attributes', {}), hashmap, restore_id)

        if 'graph' in data:
            self.getGraphScene().deserialize(data['graph'], hashmap, restore_id)

        self.refreshSourceLists()
        self.updateRemoveDeprecatedButtonState()
        self.setModified(False)
        return True
