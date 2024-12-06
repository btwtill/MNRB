from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_SINGLEDEFORMCOMPONENT, registerNode #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_NodeProperties #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_template import MNRB_NodeTemplate #type: ignore
from MNRB.MNRB_Guides.guide import guide #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

GUIDE_DEBUG = True

class MNRB_Node_SingleDeformComponent_Properties(MNRB_NodeProperties): pass


@registerNode(OPERATIONCODE_SINGLEDEFORMCOMPONENT)
class MNRB_Node_SingleDeformComponent(MNRB_NodeTemplate):
    operation_code = OPERATIONCODE_SINGLEDEFORMCOMPONENT
    operation_title = "Single_Def"
    icon = ""

    Node_Properties_Class = MNRB_Node_SingleDeformComponent_Properties

    def __init__(self, scene):
        super().__init__(scene, inputs = [["parent_ctrl", 1, False], ["parent_def", 2, False]], outputs=[["base_ctrl", 1, True], ["out_def", 2, True]])

    def guideBuild(self):
        if GUIDE_DEBUG: print("%s:: Building Guides:: " % self.__class__.__name__, self)

        if not super().guideBuild():
            return False

        self.reconstructGuides()
        
    def staticBuild(self):
        print("%s:: Building Static:: " % self)
        if not super().staticBuild():
            return False
        
        return True
    
    def componentBuild(self):
        print("%s:: Building Component:: " % self)
    
    def connectComponent(self):
        print("%s:: Connecting Component:: " % self)