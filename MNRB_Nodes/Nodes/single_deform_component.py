from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_SINGLEDEFORMCOMPONENT, registerNode #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_NodeProperties #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_template import MNRB_NodeTemplate #type: ignore
from MNRB.MNRB_Guides.guide import guide #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Deform.deform import deform #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.MNRB_Controls.control import control #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore
from MNRB.MNRB_cmds_wrapper.matrix_functions import Matrix_functions #type: ignore

GUIDE_DEBUG = False

class MNRB_Node_SingleDeformComponent_Properties(MNRB_NodeProperties): pass


@registerNode(OPERATIONCODE_SINGLEDEFORMCOMPONENT)
class MNRB_Node_SingleDeformComponent(MNRB_NodeTemplate):
    operation_code = OPERATIONCODE_SINGLEDEFORMCOMPONENT
    operation_title = "Single_Def"
    icon = ""

    Node_Properties_Class = MNRB_Node_SingleDeformComponent_Properties

    def __init__(self, scene):
        super().__init__(scene, inputs = [["parent_ctrl", SocketTypes.srt, False], ["parent_def", SocketTypes.deform, False]], outputs=[["singleDef", SocketTypes.srt, True], ["singleDef", SocketTypes.deform, True]])

    def guideBuild(self):
        if not super().guideBuild():
            return False
        
        if GUIDE_DEBUG: print("%s:: Building Guides:: " % self.__class__.__name__, self)

        self.sinlge_deform_component_guide = guide(self, name = "single")
        MC.parentObject(self.sinlge_deform_component_guide.name, self.guide_component_hierarchy)

        self.reconstructGuides()
        
        return True

    def staticBuild(self):
        if not super().staticBuild():
            return False
        
        if GUIDE_DEBUG: print("%s:: Building Static:: " % self)

        self.guide_pos = self.sinlge_deform_component_guide.getPosition()

        self.single_deform = deform(self, "singleDef")

        MC.setJointPositionMatrix(self.single_deform.name, self.guide_pos)
        MC.parentObject(self.single_deform.name, self.scene.virtual_rig_hierarchy.skeleton_hierarchy_object.name)

        return True
    
    def componentBuild(self):
        if not super().componentBuild():
            return False
        
        if GUIDE_DEBUG: print("%s:: Building Component:: " % self)

        #getting guides
        guide_pos = self.guides[0].getPosition(reset_scale = False)

        #create Inputs
        self.root_input = MC.createTransform(self.getComponentFullPrefix() + "root" + MNRB_Names.input_suffix)
        MC.parentObject(self.root_input, self.input_hierarchy)
        MC.setObjectWorldPositionMatrix(self.root_input, guide_pos)
        MC.applyTransformScale(self.root_input)

        #create controls
        self.single_control = control(self, "singleCtrl")
        Matrix_functions.setMatrixParentNoOffset(self.single_control.name, self.root_input)
        MC.parentObject(self.single_control.name, self.control_hierarchy)

        #create Outputs
        self.deform_output = MC.createTransform(self.getComponentFullPrefix() + "singleDef" + MNRB_Names.output_suffix)
        MC.parentObject(self.deform_output, self.output_hierarchy)
        Matrix_functions.decomposeTransformWorldMatrixTo(self.single_control.name, self.deform_output)
        return True
        
    def connectComponent(self):
        if not super().connectComponent():
            return False
        
        if GUIDE_DEBUG: print("%s:: Connecting Component:: " % self)
        
        srt_parent_name = self.getInputConnectionValueAt(0)
        if srt_parent_name == None:
            return False
        srt_parent =  srt_parent_name + MNRB_Names.output_suffix

        deform_parent_name = self.getInputConnectionValueAt(1)
        if deform_parent_name == None:
            return False
        deform_parent = deform_parent_name + MNRB_Names.deform_suffix

        deform_joint = self.deforms[0]

        #matrix parent with underworld Offset
        srt_parent_offset_compose_node, srt_parent_offset_mult_matrix_node = Matrix_functions.setMatrixParentWithOffset(self.root_input, srt_parent)

        #parent deform to deform parent
        MC.parentObject(deform_joint.name, deform_parent)
        deform_parent_mult_matrix_node = Matrix_functions.setLiveMatrixParentNoOffset(deform_joint.name, self.deform_output, deform_parent)

        MC.resetJointOrientations(deform_joint.name)
        return True

        