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
        if GUIDE_DEBUG: print("%s:: Building Guides:: " % self.__class__.__name__, self)

        if not super().guideBuild():
            return False
        
        self.sinlge_deform_component_guide = guide(self, name = "single")
        MC.parentObject(self.sinlge_deform_component_guide.name, self.guide_component_hierarchy)

        self.reconstructGuides()
        
    def validateGuideBuild(self):
        if not hasattr(self, 'sinlge_deform_component_guide'):
            return False
        if not self.sinlge_deform_component_guide.exists():
            return False
        return True

    def staticBuild(self):
        print("%s:: Building Static:: " % self)
        if not super().staticBuild():
            return False
        
        self.guide_pos = self.sinlge_deform_component_guide.getPosition()

        self.single_deform = deform(self, "singleDef")

        MC.setJointPositionMatrix(self.single_deform.name, self.guide_pos)
        MC.parentObject(self.single_deform.name, self.scene.virtual_rig_hierarchy.skeleton_hierarchy_object.name)

        return True
    
    def validateStaticBuild(self):
        if not hasattr(self, 'guide_pos'):
            return False
        if not hasattr(self, 'single_deform'):
            return False
        if not self.single_deform.exists():
            return False
        return True

    def componentBuild(self):
        print("%s:: Building Component:: " % self)
        if not super().componentBuild():
            return False
        
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

    def validateComponentBuild(self):
        if not hasattr(self, 'root_input'):
            return False
        if not MC.objectExists(self.root_input):
            return False
        if not hasattr(self, 'single_control'):
            return False
        if not self.single_control.exists():
            return False
        if not hasattr(self, 'deform_output'):
            return False
        if not MC.objectExists(self.deform_output):
            return False
        return True
        
    def connectComponent(self):
        print("%s:: Connecting Component:: " % self)

        srt_parent = self.getInputConnectionValueAt(0) + MNRB_Names.output_suffix
        deform_parent = self.getInputConnectionValueAt(1) + MNRB_Names.deform_suffix

        deform_joint = self.deforms[0]

        #matrix parent with underworld Offset
        srt_parent_offset_compose_node, srt_parent_offset_mult_matrix_node = Matrix_functions.setMatrixParentWithOffset(self.root_input, srt_parent)

        #parent deform to deform parent
        MC.parentObject(deform_joint.name, deform_parent)
        deform_parent_mult_matrix_node = Matrix_functions.setLiveMatrixParentNoOffset(deform_joint.name, self.deform_output, deform_parent)

        MC.resetJointOrientations(deform_joint.name)

        