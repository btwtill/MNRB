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
        super().__init__(scene, inputs = [], outputs=[["globalOffset", SocketTypes.srt, True], ["global_def", SocketTypes.deform, True]])

    def guideBuild(self):
        if not super().guideBuild():
            return False
        if GUIDE_DEBUG: print("%s:: Building Guides:: " % self.__class__.__name__, self)

        base_component_guide = guide(self, name = "global")
        MC.parentObject(base_component_guide.name, self.guide_component_hierarchy)

        self.reconstructGuides()
        
    def staticBuild(self):
        if not super().staticBuild():
            return False
        print("%s:: Building Static:: " % self.__class__.__name__, self)

        guide_pos = self.guides[0].getPosition()

        base_deform = deform(self, "global")
        MC.setJointPositionMatrix(base_deform.name, guide_pos)
        MC.parentObject(base_deform.name, self.scene.virtual_rig_hierarchy.skeleton_hierarchy_object.name)
        
        return True
    
    def componentBuild(self):
        if not super().componentBuild():
            return False
        print("%s:: Building Component:: " % self.__class__.__name__, self)
        guide_pos = self.guides[0].getPosition(reset_scale = False)

        global_control = control(self, "global",  control_type = 1)
        global_control.setPosition(guide_pos)
        global_control.setScale(2)
        MC.parentObject(global_control.name, self.control_hierarchy)
        offset_matrix_compose_node = Matrix_functions.createComposeNodeFromTransformChannelbox(global_control.name)
        Matrix_functions.setMatrixParentNoOffsetFromComposeNode(offset_matrix_compose_node, global_control.name)

        global_offset_control = control(self, "globalOffset")
        global_offset_control.setPosition(guide_pos)
        MC.parentObject(global_offset_control.name, self.control_hierarchy)
        Matrix_functions.setMatrixParentNoOffset(global_offset_control.name, global_control.name)

        #create Outputs
        global_offset_output = MC.createTransform(self.getComponentFullPrefix() + "globalOffset" + MNRB_Names.output_suffix)
        MC.parentObject(global_offset_output, self.output_hierarchy)
        Matrix_functions.decomposeTransformWorldMatrixTo(global_offset_control.name, global_offset_output)

    def connectComponent(self):
        if not super().connectComponent():
            return False
        print("%s:: Connecting Component:: " % self)

