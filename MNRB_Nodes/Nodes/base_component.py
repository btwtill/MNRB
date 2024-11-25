from PySide2.QtWidgets import QHBoxLayout, QLineEdit, QPushButton #type: ignore
from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_BASECOMPONENT, registerNode #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_Node, MNRB_NodeProperties #type: ignore


class MNRB_Node_BaseComponent_Properties(MNRB_NodeProperties):
        
    def serialize(self):
        result_data = super().serialize()
        return result_data
    
    def deserialize(self, data, hashmap = {}, restore_id=True):
        result = super().deserialize(data, hashmap, restore_id)
        return True

@registerNode(OPERATIONCODE_BASECOMPONENT)
class MNRB_Node_BaseComponent(MNRB_Node):
    operation_code = OPERATIONCODE_BASECOMPONENT
    operation_title = "Base"
    icon = "base_component.png"

    Node_Properties_Class = MNRB_Node_BaseComponent_Properties

    def __init__(self, scene):
        super().__init__(scene, inputs = [], outputs=[["base_ctrl", 1, True]])

    def guideBuild(self):
        print("%s:: Building Guides:: " % self)

    def staticBuild(self):
        print("%s:: Building Static:: " % self)
    
    def componentBuild(self):
        print("%s:: Building Component:: " % self)
    
    def connectComponent(self):
        print("%s:: Connecting Component:: " % self)