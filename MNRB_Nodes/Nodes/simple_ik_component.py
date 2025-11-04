from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_Node #type: ignore
from MNRB.MNRB_Colors.colors import MNRBColor #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_template import MNRB_NodeTemplate #type: ignore
from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_SIMPLEIKCOMPONENT, registerNode #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_NodeProperties #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket import NodeEditor_Socket #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore

class MNRB_Node_SimpleIKComponent_Properties(MNRB_NodeProperties): 

    def __init__(self, node):
        super().__init__(node)

        self.last_deform_count = 0
        self.current_deform_count  = 0

@registerNode(OPERATIONCODE_SIMPLEIKCOMPONENT)
class MNRB_Node_SimpleIKComponent(MNRB_NodeTemplate):
    operation_code = OPERATIONCODE_SIMPLEIKCOMPONENT
    operation_title = "Simple_IK"
    icon = ""

    Node_Properties_Class = MNRB_Node_SimpleIKComponent_Properties

    def __init__(self, scene,
                inputs = [
                    ["base_parent", SocketTypes.srt, False],
                    ["base_parent", SocketTypes.deform, False],
                    ["base_space", SocketTypes.space, True],
                    ["pole_space", SocketTypes.space, True],
                    ["end_space", SocketTypes.space, True],

                    ], 
                outputs=[
                        ["base", SocketTypes.srt, True],
                        ["pole", SocketTypes.srt, True],
                        ["end", SocketTypes.srt, True],

                        ["base", SocketTypes.deform, True],
                        ["pole", SocketTypes.deform, True],
                        ["end", SocketTypes.deform, True]
                        ],

                color=MNRBColor.yellow):

        super().__init__(scene, inputs, outputs, color)  # Initilize 