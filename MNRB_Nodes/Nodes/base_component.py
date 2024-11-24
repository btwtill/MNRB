from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_BASECOMPONENT, registerNode
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_Node, MNRB_NodeProperties


class MNRB_Node_BaseComponent_Properties(MNRB_NodeProperties):
    pass

@registerNode(OPERATIONCODE_BASECOMPONENT)
class MNRB_Node_BaseComponent(MNRB_Node):
    operation_code = OPERATIONCODE_BASECOMPONENT
    operation_title = "Base"

    Node_Properties_Class = MNRB_Node_BaseComponent_Properties

    def __init__(self, scene):
        super().__init__(scene, inputs = [], outputs=[["base_ctrl", 1, True]])