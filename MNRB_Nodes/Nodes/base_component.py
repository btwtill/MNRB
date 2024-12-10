from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_BASECOMPONENT, registerNode #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_NodeProperties #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_template import MNRB_NodeTemplate #type: ignore
from MNRB.MNRB_Guides.guide import guide #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.MNRB_Deform.deform import deform #type: ignore
from MNRB.MNRB_Controls.control import control #type: ignore
from MNRB.MNRB_cmds_wrapper.matrix_functions import Matrix_functions #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore
from MNRB.MNRB_cmds_wrapper.transform_functions import Transform_functions #type: ignore

GUIDE_DEBUG = True

class MNRB_Node_BaseComponent_Properties(MNRB_NodeProperties):
        
    def serialize(self):
        result_data = super().serialize()
        return result_data
    
    def deserialize(self, data, hashmap = {}, restore_id=True):
        result = super().deserialize(data, hashmap, restore_id)
        return True

@registerNode(OPERATIONCODE_BASECOMPONENT)
class MNRB_Node_BaseComponent(MNRB_NodeTemplate):
    operation_code = OPERATIONCODE_BASECOMPONENT
    operation_title = "Base"
    icon = ""

    Node_Properties_Class = MNRB_Node_BaseComponent_Properties

    def __init__(self, scene):
        super().__init__(scene, inputs = [], outputs=[["globalOffset", SocketTypes.srt, True], ["global", SocketTypes.deform, True]])

    def guideBuild(self):
        if not super().guideBuild():
            return False
        if GUIDE_DEBUG: print("%s:: Building Guides:: " % self.__class__.__name__, self)

        self.base_component_guide = guide(self, name = "global")
        MC.parentObject(self.base_component_guide.name, self.guide_component_hierarchy)

        self.reconstructGuides()
    
    def validateGuideBuild(self):
        if not hasattr(self, 'base_component_guide'):
            return False
        if not self.base_component_guide.exists():
            return False
        return True

    def staticBuild(self):
        if not super().staticBuild():
            return False
        print("%s:: Building Static:: " % self.__class__.__name__, self)

        guide_pos = self.guides[0].getPosition()

        self.base_deform = deform(self, "global")
        MC.setJointPositionMatrix(self.base_deform.name, guide_pos)
        MC.parentObject(self.base_deform.name, self.scene.virtual_rig_hierarchy.skeleton_hierarchy_object.name)
        
        return True
    
    def validateStaticBuild(self):
        if not hasattr(self, 'base_deform'):
            return False
        if not self.base_deform.exists():
            return False
        return True

    def componentBuild(self):
        #validate static Build

        if not super().componentBuild():
            return False
        print("%s:: Building Component:: " % self.__class__.__name__, self)
        self.guide_pos = self.guides[0].getPosition(reset_scale = False)

        self.global_control = control(self, "global",  control_type = 1)
        self.global_control.setPosition(self.guide_pos)
        self.global_control.setScale(2)
        MC.parentObject(self.global_control.name, self.control_hierarchy)
        offset_matrix_compose_node = Matrix_functions.createComposeNodeFromTransformChannelbox(self.global_control.name)
        Matrix_functions.setMatrixParentNoOffsetFromComposeNode(offset_matrix_compose_node, self.global_control.name)

        self.global_offset_control = control(self, "globalOffset")
        self.global_offset_control.setPosition(self.guide_pos)
        MC.parentObject(self.global_offset_control.name, self.control_hierarchy)
        Matrix_functions.setMatrixParentNoOffset(self.global_offset_control.name, self.global_control.name)

        #create Outputs
        self.global_offset_output = MC.createTransform(self.getComponentFullPrefix() + "globalOffset" + MNRB_Names.output_suffix)
        MC.parentObject(self.global_offset_output, self.output_hierarchy)
        Matrix_functions.decomposeTransformWorldMatrixTo(self.global_offset_control.name, self.global_offset_output)

    def validateComponentBuild(self):
        if not hasattr(self, 'guide_pos'):
            return False
        if not hasattr(self, ' global_control'):
            return False
        if not self.global_control.exists():
            return False
        if not hasattr(self, 'global_offset_control'):
            return False
        if not self.global_offset_control.exists():
            return False
        if not hasattr(self, 'global_offset_output'):
            return False
        if not self.global_offset_output.exists():
            return False
        return True

    def connectComponent(self):
        if not super().connectComponent():
            return False
        print("%s:: Connecting Component:: " % self)

        deform = self.deforms[0]
        Transform_functions.connectSrt(self.global_offset_output, deform.name)
        

