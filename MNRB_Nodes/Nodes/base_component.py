from PySide2.QtWidgets import QHBoxLayout, QLineEdit, QPushButton #type: ignore
from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_BASECOMPONENT, registerNode #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_Node, MNRB_NodeProperties #type: ignore


class MNRB_Node_BaseComponent_Properties(MNRB_NodeProperties):
    def initUI(self):
        super().initUI()
        self.main_geometry_label_layout = QHBoxLayout()
        self.main_geometry_name_box = QLineEdit()
        self.main_geometry_name_box.setPlaceholderText("Define you main Rig Geometry: ")

        self.main_geometry_assign_button = QPushButton("Set")
        self.main_gemotry_remove_button = QPushButton("Remove")

        self.main_geometry_label_layout.addWidget(self.main_geometry_name_box)
        self.main_geometry_label_layout.addWidget(self.main_geometry_assign_button)
        self.main_geometry_label_layout.addWidget(self.main_gemotry_remove_button)

        self.layout.addLayout(self.main_geometry_label_layout)

@registerNode(OPERATIONCODE_BASECOMPONENT)
class MNRB_Node_BaseComponent(MNRB_Node):
    operation_code = OPERATIONCODE_BASECOMPONENT
    operation_title = "Base"

    Node_Properties_Class = MNRB_Node_BaseComponent_Properties

    def __init__(self, scene):
        super().__init__(scene, inputs = [], outputs=[["base_ctrl", 1, True]])