from PySide6.QtWidgets import QCheckBox #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_NodeProperties import NodeEditorNodeProperties #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_Socket import LEFT #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_StepGraphicNode import PipelineStep_QGraphicNode #type: ignore

CLASS_DEBUG = False

class PipelineStepProperties(NodeEditorNodeProperties):
    def __init__(self, node):
        super().__init__(node)

        self.is_disabled = False
        #unlike a rig component, a pipeline step has no name-uniqueness/required-field
        #validation in this pass - nothing would ever set this True otherwise, and
        #every step's corner icon would show permanently invalid
        self.is_valid = True

    def initUI(self):
        self.disabled_checkbox = QCheckBox("Disable Step")
        self.disabled_checkbox.stateChanged.connect(self.updateDisabledState)
        self.disabled_checkbox.stateChanged.connect(self.setHasBeenModified)
        self.layout.addWidget(self.disabled_checkbox)

    def updateDisabledState(self):
        self.is_disabled = self.disabled_checkbox.isChecked()

    def serialize(self):
        result_data = super().serialize()
        result_data['is_disabled'] = self.is_disabled
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id=True):
        result = super().deserialize(data, hashmap, restore_id)
        self.is_disabled = data.get('is_disabled', False)
        self.disabled_checkbox.setChecked(self.is_disabled)
        return True


class PipelineStepNode(NodeEditorNode):
    """Base for a build-pipeline step - a thin wrapper around one tab's existing
    build method(s). Not meant to be used directly; concrete steps (pipeline_Editor_UI/steps/)
    override runStep()."""

    operation_code = 0
    operation_title = "PipelineStep"
    icon = ""
    Node_Properties_Class = PipelineStepProperties
    Graphics_Node_Class = PipelineStep_QGraphicNode

    def __init__(self, scene, inputs = [["In", SocketTypes.sequence, True]], outputs = [["Out", SocketTypes.sequence, True]]):
        super().__init__(scene, self.__class__.operation_title, inputs, outputs)

    def getSocketPosition(self, index, position):
        #every step has exactly one input and one output, both vertically centered
        #on the node - not stacked by index/count like rig-component sockets
        x = 0 if position == LEFT else self.grNode.width
        y = self.grNode.height / 2
        return [x, y]

    def runStep(self):
        """Returns (success: bool, message: str). Override in concrete step types."""
        return False, "runStep() not implemented for %s" % self.__class__.__name__

    def serialize(self):
        result_data = super().serialize()
        result_data['operation_code'] = self.__class__.operation_code
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id = True, exists = False):
        return super().deserialize(data, hashmap, restore_id, exists)
