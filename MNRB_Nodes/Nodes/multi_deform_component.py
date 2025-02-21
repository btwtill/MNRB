from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_Node #type: ignore
from MNRB.MNRB_Colors.colors import MNRBColor #type: ignore
from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_MULTIDEFORMCOMPONENT, registerNode #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_template import MNRB_NodeTemplate #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_NodeProperties #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore

class MNRB_Node_MultiDeformComponent_Properties(MNRB_NodeProperties): pass

@registerNode(OPERATIONCODE_MULTIDEFORMCOMPONENT)
class MNRB_Node_MultiDeformComponent(MNRB_NodeTemplate):
    operation_code = OPERATIONCODE_MULTIDEFORMCOMPONENT
    operation_title = "Multi"
    icon = ""

    Node_Properties_Class = MNRB_Node_MultiDeformComponent_Properties

    def __init__(self, scene, 
                inputs = [], 
                outputs=[["globalOffset", SocketTypes.srt, True], ["global", SocketTypes.deform, True]], 
                color=MNRBColor.yellow):
        super().__init__(scene, inputs, outputs, color)

    def guideBuild(self):
        return super().guideBuild()
    
    def staticBuild(self):
        return super().staticBuild()

    def componentBuild(self):
        return super().componentBuild()

    def connectComponent(self):
        return super().connectComponent()