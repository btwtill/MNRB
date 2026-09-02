from PySide6 import QtWidgets #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicView import NodeEditor_QGraphicView #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge import NodeEditor_QGraphicEdge #type: ignore
from MNRB.MNRB_UI.pipeline_Editor_UI.pipeline_Editor_Scene import PipelineEditorScene #type: ignore
from MNRB.MNRB_UI.pipeline_Editor_UI.pipeline_Editor_StepNode import PipelineStepNode #type: ignore
from MNRB.MNRB_UI.pipeline_Editor_UI.pipeline_Editor_conf import PIPELINE_STEPS, getClassFromOperationCode #type: ignore

CLASS_DEBUG = False
CONTEXT_DEBUG = False

class PipelineEditorWidget(QtWidgets.QWidget):
    """Mirrors NodeEditorWidget's shape (node_Editor_UI/node_Editor_Widget.py) but
    wired to the pipeline-step registry instead of MNRB_NODES, and without the
    guide/static/component/connect context menu, which is rig-specific."""

    def __init__(self, property_widget = None, node_editor_tab = None, skinning_tab = None, parent=None):
        super().__init__(parent)

        self.property_widget = property_widget

        self.initUI(node_editor_tab, skinning_tab)
        self.initCallbacks()
        self.scene.setNodeClassSelectorFunction(self.getNodeClassFromData)

    def initUI(self, node_editor_tab, skinning_tab):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.scene = PipelineEditorScene(node_editor_tab, skinning_tab)

        self.view = NodeEditor_QGraphicView(self.scene.grScene, self)
        self.layout.addWidget(self.view)

        self.updatePropertyWindow()

    def initCallbacks(self):
        self.scene.connectItemSelectedListenerCallback(self.updatePropertyWindow)
        self.scene.connectItemsDeselectedListenerCallback(self.updatePropertyWindow)

    def centerView(self):
        self.view.centerView()

    def sceneHasSelectedItems(self):
        return self.getSelectedItems() != []

    def getSelectedItems(self):
        return self.scene.getSelectedItems()

    def getNodeClassFromData(self, data):
        if 'operation_code' not in data: return PipelineStepNode
        return getClassFromOperationCode(data['operation_code'])

    def updatePropertyWindow(self):
        selected_items = self.getSelectedItems()

        if selected_items == []:
            self.property_widget.setWidget(self.scene.properties)
            self.property_widget.setWindowTitle(self.scene.properties.title)
        elif len(selected_items) == 1:
            active_widget = selected_items[0]
            if hasattr(active_widget, 'node'):
                self.property_widget.setWidget(active_widget.node.properties)
                self.property_widget.setWindowTitle(active_widget.node.properties.title)
            elif isinstance(active_widget, NodeEditor_QGraphicEdge):
                self.property_widget.setWidget(active_widget.edge.properties)
                self.property_widget.setWindowTitle(active_widget.edge.properties.title)
        else:
            #no multi-edit properties widget for pipeline steps in this pass -
            #just show the first selected step's properties
            filtered_selection = [item for item in selected_items if hasattr(item, 'node')]
            if filtered_selection:
                active_widget = filtered_selection[0]
                self.property_widget.setWidget(active_widget.node.properties)
                self.property_widget.setWindowTitle(active_widget.node.properties.title)

    def contextMenuEvent(self, event):
        item = self.scene.getItemAt(event.pos())
        if type(item) == QtWidgets.QGraphicsProxyWidget:
            item = item.widget()

        if not (hasattr(item, 'node') or hasattr(item, 'socket') or hasattr(item, 'edge')):
            self.handleNewStepContextMenu(event)

        return super().contextMenuEvent(event)

    def handleNewStepContextMenu(self, event):
        context_menu = QtWidgets.QMenu(self)
        action_by_code = {}

        for operation_code in sorted(PIPELINE_STEPS.keys()):
            step_class = PIPELINE_STEPS[operation_code]
            action_by_code[operation_code] = context_menu.addAction(step_class.operation_title)

        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return

        for operation_code, candidate_action in action_by_code.items():
            if candidate_action == action:
                new_node = PIPELINE_STEPS[operation_code](self.scene)
                scene_position = self.scene.getView().mapToScene(event.pos())
                new_node.setPosition(scene_position.x(), scene_position.y())
                self.scene.history.storeHistory("Created New Step", set_modified=True)
                break

    def __str__(self): return "ClassInstance::%s::  %s..%s" % (self.__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])
