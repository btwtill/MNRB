from PySide2.QtWidgets import QVBoxLayout, QLabel, QLineEdit #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_NodeProperties import NodeEditorNodeProperties #type: ignore

class MNRB_NodeProperties(NodeEditorNodeProperties):
    def initUI(self):
        self.component_name_edit = QLineEdit()
        self.component_name_edit.setPlaceholderText("Enter Component Name: ")
        self.layout.addWidget(self.component_name_edit)
        self.layout.addStretch()

class MNRB_Node(NodeEditorNode):
    operation_code = 0
    operation_title = "MNRB_Node"
    icon = None

    Node_Properties_Class = MNRB_NodeProperties

    def __init__(self, scene, inputs=[], outputs=[]):
        super().__init__(scene, self.__class__.operation_title, inputs, outputs)
        self.value = None

    def serialize(self):
        result_data = super().serialize()
        result_data['operation_code'] = self.__class__.operation_code
        return result_data
    
    def deserialize(self, data, hashmap={}, restore_id = True, exists=False):
        result = super().deserialize(data, hashmap, restore_id, exists)

        return True