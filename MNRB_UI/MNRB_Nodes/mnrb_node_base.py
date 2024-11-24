from PySide2.QtWidgets import QVBoxLayout, QLabel, QLineEdit #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_NodeProperties import NodeEditorNodeProperties #type: ignore

class MNRB_NodeProperties(NodeEditorNodeProperties):
    def initUI(self):
        self.component_name_edit = QLineEdit()
        self.component_name_edit.setPlaceholderText("Enter Component Name: ")
        self.layout.addStretch()

class MNRB_Node(NodeEditorNode):
    operation_code = 0
    operation_title = "Undefined"

    Node_Properties_Class = MNRB_NodeProperties

    def __init__(self, scene, inputs=[], outputs=[]):
        super().__init__(scene, self.__class__.operation_title, inputs, outputs)
