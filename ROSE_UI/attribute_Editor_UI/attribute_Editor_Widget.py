from PySide6 import QtWidgets #type: ignore
from PySide6.QtCore import Qt #type: ignore
from MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicView import NodeEditor_QGraphicView #type: ignore
from MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge import NodeEditor_QGraphicEdge #type: ignore
from MNRB.ROSE_UI.UI_GraphicComponents.drag_payload import decodeIdNamePayload #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_Scene import AttributeEditorScene #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_SourceList import ATTRIBUTE_MIMETYPE, CONTROL_MIMETYPE #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_conf import (ATTRIBUTE_NODES, ATTRIBUTE_NODE_GROUPS, #type: ignore
                                                                    getClassFromOperationCode,
                                                                    OPERATIONCODE_ATTRIBUTE_NODE,
                                                                    OPERATIONCODE_CONTROL_NODE)
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_Node import AttributeGraphNode #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")
dragdrop_log = ROSE_Log.get("rose.node_editor.dragdrop")

class AttributeEditorWidget(QtWidgets.QWidget):
    """The attribute canvas - same shape as PipelineEditorWidget, wired to the
    attribute-node registry and accepting drops from the tab's two source lists."""

    def __init__(self, tab, property_widget = None, parent = None):
        super().__init__(parent)

        self.tab = tab
        self.property_widget = property_widget

        self.initUI()
        self.initCallbacks()
        self.scene.setNodeClassSelectorFunction(self.getNodeClassFromData)

    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.scene = AttributeEditorScene(self.tab)

        self.view = NodeEditor_QGraphicView(self.scene.grScene, self)
        self.view.setAcceptDrops(True)
        self.layout.addWidget(self.view)

        #straight onto the view: those two convenience forwarders live on
        #NodeEditorScene, which this scene deliberately isn't a subclass of
        self.view.connectViewDragEnterListenerCallback(self.onDragEnter)
        self.view.connectViewDropListenerCallback(self.onDrop)

        self.updatePropertyWindow()

    def initCallbacks(self):
        self.scene.connectItemSelectedListenerCallback(self.updatePropertyWindow)
        self.scene.connectItemsDeselectedListenerCallback(self.updatePropertyWindow)
        #an edge added or removed changes what is driven by what, and therefore
        #which nodes are valid - revalidate on every graph change
        self.scene.connectSceneChangedCallback(self.scene.validateAllNodes)

    def centerView(self):
        self.view.centerView()

    def getNodeClassFromData(self, data):
        if 'operation_code' not in data:
            return AttributeGraphNode
        return getClassFromOperationCode(data['operation_code'])

    def getSelectedItems(self):
        return self.scene.getSelectedItems()

    def sceneHasSelectedItems(self):
        return self.getSelectedItems() != []

# Drops from the source lists

    def onDragEnter(self, event):
        if (event.mimeData().hasFormat(ATTRIBUTE_MIMETYPE)
                or event.mimeData().hasFormat(CONTROL_MIMETYPE)):
            event.acceptProposedAction()
        else:
            event.setAccepted(False)

    def onDrop(self, event):
        mime_data = event.mimeData()

        if mime_data.hasFormat(ATTRIBUTE_MIMETYPE):
            entries = decodeIdNamePayload(mime_data.data(ATTRIBUTE_MIMETYPE))
            self.addNodesForEntries(entries, OPERATIONCODE_ATTRIBUTE_NODE, event)
        elif mime_data.hasFormat(CONTROL_MIMETYPE):
            entries = decodeIdNamePayload(mime_data.data(CONTROL_MIMETYPE))
            self.addNodesForEntries(entries, OPERATIONCODE_CONTROL_NODE, event)
        else:
            event.ignore()
            return

        event.setDropAction(Qt.CopyAction)
        event.accept()

    def addNodesForEntries(self, entries, operation_code, event):
        scene_position = self.view.mapToScene(event.pos())
        rig_scene = self.scene.getRigScene()
        node_class = getClassFromOperationCode(operation_code)

        for index, (entry_id, entry_name) in enumerate(entries):
            new_node = node_class(self.scene)
            #stacked rather than piled on one point, so a group drop is readable
            new_node.setPosition(scene_position.x(), scene_position.y() + index * 90)

            if operation_code == OPERATIONCODE_ATTRIBUTE_NODE:
                #id only: the palette listed these from live objects a moment ago,
                #so the id is current. A name fallback here would let a rig-root
                #attribute be resolved to a same-named component attribute.
                component_attribute = self.scene.findAttributeById(entry_id)

                if component_attribute is None:
                    dragdrop_log.debug("ATTRIBUTEEDITORWIDGET:: unresolved attribute", entry_name)
                    new_node.remove()
                    continue
                new_node.setAttributeRef(component_attribute)
            else:
                control = None
                if rig_scene is not None:
                    control = rig_scene.getControlById(entry_id) or rig_scene.getControlByName(entry_name)
                if control is None:
                    dragdrop_log.debug("ATTRIBUTEEDITORWIDGET:: unresolved control", entry_name)
                    new_node.remove()
                    continue
                new_node.setControlRef(control)

        self.scene.validateAllNodes()
        self.scene.history.storeHistory("Added Node(s)", set_modified = True)

# Operators via the canvas context menu

    def contextMenuEvent(self, event):
        item = self.scene.getItemAt(event.pos())
        if type(item) == QtWidgets.QGraphicsProxyWidget:
            item = item.widget()

        if not (hasattr(item, 'node') or hasattr(item, 'socket') or hasattr(item, 'edge')):
            self.handleNewOperatorContextMenu(event)

        return super().contextMenuEvent(event)

    def handleNewOperatorContextMenu(self, event):
        context_menu = QtWidgets.QMenu(self)
        action_by_code = {}

        #every group, not just the first - Targets would otherwise never appear.
        #Attribute and Control nodes are deliberately absent: they come from the
        #palettes, so they can never exist without something real behind them.
        for group_key in sorted(ATTRIBUTE_NODE_GROUPS.keys()):
            group_label, operation_codes = ATTRIBUTE_NODE_GROUPS[group_key]
            submenu = context_menu.addMenu(group_label)
            for operation_code in operation_codes:
                node_class = ATTRIBUTE_NODES.get(operation_code)
                if node_class is None:
                    continue
                action_by_code[operation_code] = submenu.addAction(node_class.operation_title)

        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return

        for operation_code, candidate in action_by_code.items():
            if candidate == action:
                new_node = ATTRIBUTE_NODES[operation_code](self.scene)
                scene_position = self.view.mapToScene(event.pos())
                new_node.setPosition(scene_position.x(), scene_position.y())
                self.scene.validateAllNodes()
                self.scene.history.storeHistory("Created Operator", set_modified = True)
                break

    def updatePropertyWindow(self):
        if self.property_widget is None:
            return

        selected_items = self.getSelectedItems()

        if selected_items == []:
            self.property_widget.setWidget(self.scene.properties)
            self.property_widget.setWindowTitle("Attribute Graph")
            return

        active_widget = selected_items[0]
        if hasattr(active_widget, 'node'):
            active_widget.node.properties.refresh()
            self.property_widget.setWidget(active_widget.node.properties)
            self.property_widget.setWindowTitle(active_widget.node.title)
        elif isinstance(active_widget, NodeEditor_QGraphicEdge):
            self.property_widget.setWidget(active_widget.edge.properties)
            self.property_widget.setWindowTitle(active_widget.edge.properties.title)
