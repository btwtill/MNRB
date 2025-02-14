import os
from PySide2 import QtWidgets # type: ignore
from PySide2.QtGui import QIcon #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicView import NodeEditor_QGraphicView # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Scene import NodeEditorScene # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge import NodeEditor_QGraphicEdge #type: ignore
from MNRB.MNRB_Nodes.node_Editor_conf import getClassFromOperationCode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge import EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT #type: ignore
from MNRB.MNRB_Nodes.node_Editor_conf import MNRB_NODES #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_DragNodeList import ICONPATH #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_multiEditPropertiesWidget import MultiEdit_PropertyWidget #type: ignore

CLASS_DEBUG = False
CONTEXT_DEBUG = False

class NodeEditorWidget(QtWidgets.QWidget):
    def __init__(self, property_widget = None, parent=None):
        super().__init__(parent)
        if CLASS_DEBUG : print("NODE_EDITOR_WIDGET:: -__init__:: Initialized Node Editor Widget")

        self.property_widget = property_widget

        self.initUI()
        self.initNewNodeActions()
        self.initCallbacks()
        self.scene.setNodeClassSelectorFunction(self.getNodeClassFromData)

    def initUI(self):

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout (self.layout)

        self.scene = NodeEditorScene()

        self.view = NodeEditor_QGraphicView(self.scene.grScene, self)
        self.layout.addWidget(self.view)

        self.updatePropertyWindow()

    def initCallbacks(self):
        self.scene.connectItemSelectedListenerCallback(self.updatePropertyWindow)
        self.scene.connectItemsDeselectedListenerCallback(self.updatePropertyWindow)

    def initNodesContextMenu(self):
        context_menu = QtWidgets.QMenu(self)
        keys = list(MNRB_NODES.keys())
        keys.sort()
        for key in keys: context_menu.addAction(self.node_actions[key])
        return context_menu

    def initNewNodeActions(self):
        self.node_actions = {}
        keys = list(MNRB_NODES.keys())
        keys.sort()
        for key in keys:
            node = MNRB_NODES[key]
            icon_path = os.path.join(ICONPATH, node.icon) if node.icon != "" else os.path.join(ICONPATH, "default_node.png")
            self.node_actions[node.operation_code] = QtWidgets.QAction(QIcon(icon_path), node.operation_title)
            self.node_actions[node.operation_code].setData(node.operation_code)

    def centerView(self):
        self.view.centerView()

    def sceneHasSelectedItems(self):
        return self.getSelectedItems() != []
    
    def getSelectedItems(self):
        return self.scene.getSelectedItems()

    def getNodeClassFromData(self, data):
        if 'operation_code' not in data: return NodeEditorNode
        return getClassFromOperationCode(data['operation_code'])

    def updatePropertyWindow(self):
        if CLASS_DEBUG: print("NODEEDITORWIDGET:: --updatePropertyWindow:: Updating Property Window!!")
        selected_items = self.getSelectedItems()

        if selected_items == []:
            if CLASS_DEBUG: print("NODEEDITORWIDGET:: --updatePropertyWindow:: Selected Items:: ", selected_items)
            if CLASS_DEBUG: print("NODEEDITORWIDGET:: --updatePropertyWindow:: setting Dock Widget to:: ", self.scene.properties)
            
            self.property_widget.setWidget(self.scene.properties)
            self.property_widget.setWindowTitle(self.scene.properties.title)
        elif len(selected_items) == 1:
            active_widget = selected_items[0]
            if CLASS_DEBUG: print("NODEEDITORWIDGET:: --updatePropertyWindow:: setting Dock Widget to First in Selection:: ", active_widget)
            if hasattr(active_widget, 'node'):
                self.property_widget.setWidget(active_widget.node.properties)
                self.property_widget.setWindowTitle(active_widget.node.properties.title)
            elif isinstance(active_widget, NodeEditor_QGraphicEdge):
                self.property_widget.setWidget(active_widget.edge.properties)
                self.property_widget.setWindowTitle(active_widget.edge.properties.title)
        else:
            print("NODEEDITORWIDGET:: --updatePropertyWindow:: Multi Selection Properties Window!!")
            multi_edit_property_widget = MultiEdit_PropertyWidget(selected_items)
            self.property_widget.setWidget(multi_edit_property_widget)
            self.property_widget.setWindowTitle(multi_edit_property_widget.title)

    def contextMenuEvent(self, event):
        item  = self.scene.getItemAt(event.pos())
        if CONTEXT_DEBUG: print("NODE_EDITOR_TAB:: --contextMenuEvent:: Item At Context Menu Event:: ", item)
        if type(item) == QtWidgets.QGraphicsProxyWidget:
            item = item.widget()

        if hasattr(item, 'node') or hasattr(item, 'socket'):
            self.handleNodeContextMenu(event)
        elif hasattr(item, 'edge'):
            self.handleEdgeContextMenu(event)
        else:
            self.handleNewNodeContextMenu(event)

        return super().contextMenuEvent(event)

    def handleNodeContextMenu(self, event):
        if CONTEXT_DEBUG: print("NODE_EDITOR_TAB:: --handleNodeContextMenu:: Node Context Menu Open:: ")
        context_menu = QtWidgets.QMenu(self)

        evaluate_properties = context_menu.addAction("validate")
        build_guides = context_menu.addAction("build guides")
        build_static = context_menu.addAction("build static")
        build_component = context_menu.addAction("build component")
        build_connected = context_menu.addAction("build connected")
        context_menu.addSeparator()
        select_guides = context_menu.addAction("Select Guides")
        select_deforms = context_menu.addAction("Select Deforms")

        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item  = self.scene.getItemAt(event.pos())
        if type(item) == QtWidgets.QGraphicsProxyWidget:
            item = item.widget()

        if hasattr(item, 'node'):
            selected = item.node
        
        if hasattr(item, 'socket'):
            selected = item.socket.node

        if CONTEXT_DEBUG: print("NODE_EDITOR_TAB:: --handleNodeContextMenu:: got item:: ", selected)

        if selected and action == evaluate_properties: selected.properties.validateProperties() if not selected.properties.is_disabled else print("Disabled")
        if selected and action == build_guides: selected.guideBuild() if not selected.properties.is_disabled else print("Disabled")
        if selected and action == build_static: selected.staticBuild() if not selected.properties.is_disabled else print("Disabled")
        if selected and action == build_component: selected.componentBuild() if not selected.properties.is_disabled else print("Disabled")
        if selected and action == build_connected: selected.connectComponent() if not selected.properties.is_disabled else print("Disabled")
        if selected and action == select_guides: selected.selectAllGuides()
        if selected and action == select_deforms: selected.selectAllDeforms()

    def handleEdgeContextMenu(self, event):
        if CONTEXT_DEBUG: print("NODE_EDITOR_TAB:: --handleNodeContextMenu:: Edge Context Menu Open:: ")

        context_menu = QtWidgets.QMenu(self)
        bezier_action = context_menu.addAction("Bezier")
        direct_action = context_menu.addAction("Direct")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.getItemAt(event.pos())

        if hasattr(item, 'edge'):
            selected = item.edge

        if selected and action == bezier_action: selected.edge_type = EDGE_TYPE_BEZIER
        if selected and action == direct_action: selected.edge_type = EDGE_TYPE_DIRECT

    def handleNewNodeContextMenu(self, event):
        if CONTEXT_DEBUG: print("NODE_EDITOR_TAB:: --handleNodeContextMenu:: New Node Context Menu Open:: ")
        context_menu = self.initNodesContextMenu()

        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action is not None:
            new_node = getClassFromOperationCode(action.data())(self.scene)
            scene_position = self.scene.getView().mapToScene(event.pos())
            new_node.setPosition(scene_position.x(), scene_position.y())

    def __str__(self): return "ClassInstance::%s::  %s..%s" % (self.__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])