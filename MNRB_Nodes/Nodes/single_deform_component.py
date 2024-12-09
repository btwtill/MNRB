from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_SINGLEDEFORMCOMPONENT, registerNode #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_NodeProperties #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_template import MNRB_NodeTemplate #type: ignore
from MNRB.MNRB_Guides.guide import guide #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore
from MNRB.MNRB_Deform.deform import deform #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore

GUIDE_DEBUG = True

class MNRB_Node_SingleDeformComponent_Properties(MNRB_NodeProperties): pass


@registerNode(OPERATIONCODE_SINGLEDEFORMCOMPONENT)
class MNRB_Node_SingleDeformComponent(MNRB_NodeTemplate):
    operation_code = OPERATIONCODE_SINGLEDEFORMCOMPONENT
    operation_title = "Single_Def"
    icon = ""

    Node_Properties_Class = MNRB_Node_SingleDeformComponent_Properties

    def __init__(self, scene):
        super().__init__(scene, inputs = [["parent_ctrl", SocketTypes.srt, False], ["parent_def", SocketTypes.deform, False]], outputs=[["singleDef_ctrl", SocketTypes.srt, True], ["singleDef_srt", SocketTypes.deform, True]])

    def guideBuild(self):
        if GUIDE_DEBUG: print("%s:: Building Guides:: " % self.__class__.__name__, self)

        if not super().guideBuild():
            return False
        
        self.sinlge_deform_component_guide = guide(self, name = "single")
        MC.parentObject(self.sinlge_deform_component_guide.name, self.guide_component_hierarchy)

        self.reconstructGuides()
        
    def staticBuild(self):
        print("%s:: Building Static:: " % self)
        if not super().staticBuild():
            return False
        
        guide_pos = self.sinlge_deform_component_guide.getPosition()

        single_deform = deform(self, "singleDef")

        MC.setJointPositionMatrix(single_deform.name, guide_pos)
        MC.parentObject(single_deform.name, self.scene.virtual_rig_hierarchy.skeleton_hierarchy_object.name)

        return True
    
    def componentBuild(self):
        print("%s:: Building Component:: " % self)
        super().componentBuild()   
        
    def connectComponent(self):
        print("%s:: Connecting Component:: " % self)