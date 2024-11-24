from PySide2 import QtWidgets # type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicView import NodeEditor_QGraphicView # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Scene import NodeEditorScene # type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge import NodeEditorEdge#type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge import NodeEditor_QGraphicEdge #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicNode import NodeEditor_QGraphicNode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge import EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER #type: ignore

CLASS_DEBUG = True

class NodeEditorWidget(QtWidgets.QWidget):
    def __init__(self, property_widget = None, parent=None):
        super().__init__(parent)
        if CLASS_DEBUG : print("NODE_EDITOR_WIDGET:: -__init__:: Initialized Node Editor Widget")

        self.property_widget = property_widget

        self.initUI()
        self.initCallbacks()
        #debug use only remove later
        #self.addTestContent()

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

    def addTestContent(self):
        content_node_01 = NodeEditorNode(self.scene, title = "Node 01", inputs = [["input 01", 0, False]], outputs=[["output 01", 3, False]] )
        content_node_02 = NodeEditorNode(self.scene, title = "Node 02", inputs = [["arm_def",0, True],["arm_ctrl",0, False]], outputs=[["arm_def",1, True],["arm_ctrl",1, True]] )

        content_node_01.setPosition(-120, 20)
        content_node_02.setPosition(140, -20)

        content_edge_01 = NodeEditorEdge(self.scene, content_node_01.outputs[0], content_node_02.inputs[0], edge_type = EDGE_TYPE_BEZIER)

        content_edge_02 = NodeEditorEdge(self.scene, content_node_01.outputs[0], content_node_02.inputs[1], edge_type = EDGE_TYPE_BEZIER)

    def centerView(self):
        self.view.centerView()

    def sceneHasSelectedItems(self):
        return self.getSelectedItems() != []
    
    def getSelectedItems(self):
        return self.scene.getSelectedItems()

    def updatePropertyWindow(self):
        if CLASS_DEBUG: print("NODEEDITORWIDGET:: --updatePropertyWindow:: Updating Property Window!!")
        selected_items = self.getSelectedItems()

        if selected_items == []:
            if CLASS_DEBUG: print("NODEEDITORWIDGET:: --updatePropertyWindow:: Selected Items:: ", selected_items)
            if CLASS_DEBUG: print("NODEEDITORWIDGET:: --updatePropertyWindow:: setting Dock Widget to:: ", self.scene.properties)
            
            self.property_widget.setWidget(self.scene.properties)
            self.property_widget.setWindowTitle(self.scene.properties.title)
        else:
            active_widget = selected_items[0]
            if CLASS_DEBUG: print("NODEEDITORWIDGET:: --updatePropertyWindow:: setting Dock Widget to First in Selection:: ", active_widget)
            if hasattr(active_widget, 'node'):
                self.property_widget.setWidget(active_widget.node.properties)
                self.property_widget.setWindowTitle(active_widget.node.properties.title)
            elif isinstance(active_widget, NodeEditor_QGraphicEdge):
                self.property_widget.setWidget(active_widget.edge.properties)
                self.property_widget.setWindowTitle(active_widget.edge.properties.title)