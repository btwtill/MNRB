import math
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_Node #type: ignore
from MNRB.MNRB_Colors.colors import MNRBColor #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_template import MNRB_NodeTemplate #type: ignore
from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_SIMPLEIKCOMPONENT, registerNode #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_NodeProperties #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket import NodeEditor_Socket #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.MNRB_Guides.guide import guide #type: ignore
from MNRB.MNRB_Deform.deform import deform #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore
from MNRB.MNRB_Controls.control import control #type: ignore
from MNRB.MNRB_cmds_wrapper.matrix_functions import Matrix_functions #type: ignore

GUIDE_DEBUG = True
CLASS_DEBUG = True

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
                    ["base", SocketTypes.srt, False],
                    ["base", SocketTypes.deform, False],
                    ["ik", SocketTypes.srt, False]
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

    def guideBuild(self):
        '''
        Build all guide object of this component
            * Base Guide - start of the IK chain
            * Pole Guide - Pole target of the IK chain
            * End Guide - End of the IK Chain
        '''

        if not super().guideBuild():    # Check if the basic guide Strucutre is successfully build and only then continue
            return False
        
        if GUIDE_DEBUG: print("%s:: Building Guides:: " % self.__class__.__name__, self)
        
        # Create Base Guide
        baseGuide = guide(self, "base")

        MC.parentObject(baseGuide.name, self.guide_component_hierarchy) # Parent baseGuide to guide hierarchy

        # Create Pole Guide
        poleGuide = guide(self, "pole", baseGuide)

        MC.parentObject(poleGuide.name, baseGuide.name)
        MC.clearTransforms(poleGuide.name)
        MC.addTranslation(poleGuide.name, 0.5, 0.0, 0.0)

        # Create End Guide
        endGuide = guide(self, "end", poleGuide)
        
        MC.parentObject(endGuide.name, poleGuide.name)
        MC.clearTransforms(endGuide.name)
        MC.addTranslation(endGuide.name, 0.5, 0.0, 0.0)

        self.reconstructGuides() # Reposition and construct guides that have been lost but user wants to restore

        return True
    
    def staticBuild(self) -> bool:
        '''
        Build the Static deform objects of this component without connection to any input or output object
        '''
        if not super().staticBuild():   # Check if the basic structure of the static build exists and only then continue building
            return False
        
        if GUIDE_DEBUG: print("%s:: Building Static :: " % self.__class__.__name__, self)

        for index, guide in enumerate(self.guides):
            guide_pos = guide.getPosition()

            new_deform = deform(self, guide.guide_name)     # Create new deformation joint
            new_deform.setPosition(guide_pos)               # Set new deformation joint position
            new_deform.setSegmentScaleCompensate(False)     # Disable segment scale

            if index > 0:                                   # If there is more then one guide parent each new one to the previous one
                parent_deform = self.deforms[index - 1]
                MC.parentObject(new_deform.name, parent_deform.name)
            else:
                MC.parentObject(new_deform.name, self.scene.virtual_rig_hierarchy.skeleton_hierarchy_object.name)

        return True

    def componentBuild(self):
        '''
        Build function creating all internal logic for the component, controls and kinematics
        '''
        if not super().componentBuild():  # If base component build setup is not working return false otherwise continue component build
            return False
        
        if CLASS_DEBUG: print("%s:: Building Component :: " % self.__class__.__name__, self)

        # Get component guide positions

        base_guide_position = self.guides[0].getPosition()          # Base guide transform Matrix
        pole_guide_position = self.guides[1].getPosition()          # Pole guide transform Matrix
        end_guide_position = self.guides[2].getPosition()           # End guide transform Matrix

        # Create Main Inputs
        # Base Input
        self.base_input = MC.createTransform(self.getComponentFullPrefix() + "base" + MNRB_Names.input_suffix)
        MC.parentObject(self.base_input, self.input_hierarchy)
        MC.setObjectWorldPositionMatrix(self.base_input, base_guide_position)
        MC.applyTransformScale(self.base_input)

        pole_position = self.calculate_pole_vector_position(base_guide_position, pole_guide_position, end_guide_position, 5)

        # Pole Input -> Created here because it needs the pole control position for correct placement
        self.pole_input = MC.createTransform(self.getComponentFullPrefix() + "pole" + MNRB_Names.input_suffix)
        MC.parentObject(self.pole_input, self.input_hierarchy)
        MC.setTranslation(self.pole_input, *pole_position)

        # End Input
        self.end_input = MC.createTransform(self.getComponentFullPrefix() + "end" + MNRB_Names.input_suffix)
        MC.parentObject(self.end_input, self.input_hierarchy)
        MC.setObjectWorldPositionMatrix(self.end_input, end_guide_position)
        MC.applyTransformScale(self.end_input)

        # Create Controls
        # IK Base (start) Control
        base_control = control(self, "base")
        Matrix_functions.setMatrixParentNoOffset(base_control.name, self.base_input)
        MC.parentObject(base_control.name, self.control_hierarchy)

        # IK Pole (polevector) control
        pole_control = control(self, "pole")
        MC.parentObject(pole_control.name, self.control_hierarchy)
        Matrix_functions.setMatrixParentNoOffset(pole_control.name, self.pole_input)

        # IK end control
        end_control = control(self, "end")
        Matrix_functions.setMatrixParentNoOffset(end_control.name, self.end_input)
        MC.parentObject(end_control.name, self.control_hierarchy)

        # Create IK Joint Chain
        # Create IK Hierarchy

        ik_system_hierarchy = MC.createTransform("ik_system")
        MC.parentObject(ik_system_hierarchy, self.system_hierarchy)

        # Create Base Ik Joint
        base_ik_joint = MC.createJoint(self.getComponentFullPrefix() + "base_forward_ik")
        MC.parentObject(base_ik_joint, ik_system_hierarchy)
 
        MC.setObjectWorldPositionMatrix(base_ik_joint, base_guide_position)     # Set joint position
        MC.applyTransformRotate(base_ik_joint)                                  # Zero out Rotation 
        MC.applyTransformScale(base_ik_joint)                                   # Unify scale to 111

        # Create pole Ik Joint
        pole_ik_joint = MC.createJoint(self.getComponentFullPrefix() + "pole_forward_ik")
        MC.parentObject(pole_ik_joint, base_ik_joint)

        MC.setObjectWorldPositionMatrix(pole_ik_joint, pole_guide_position)     # Set joint position
        MC.applyTransformRotate(pole_ik_joint)                                  # Zero out Rotation 
        MC.applyTransformScale(pole_ik_joint)                                   # Unify scale to 111

        # Create end Ik Joint
        end_ik_joint = MC.createJoint(self.getComponentFullPrefix() + "end_forward_ik")
        MC.parentObject(end_ik_joint, pole_ik_joint)

        MC.setObjectWorldPositionMatrix(end_ik_joint, end_guide_position)      # Set joint position
        MC.applyTransformRotate(end_ik_joint)                                  # Zero out Rotation 
        MC.applyTransformScale(end_ik_joint)                                   # Unify scale to 111

        # Create Outputs
        # Create IK Base (start) outputs
        base_output = MC.createTransform(self.getComponentFullPrefix() + "base" + MNRB_Names.output_suffix)
        Matrix_functions.decomposeTransformWorldMatrixTo(base_ik_joint, base_output)
        MC.parentObject(base_output, self.output_hierarchy)

        # Create IK Pole output
        pole_output = MC.createTransform(self.getComponentFullPrefix() + "pole" + MNRB_Names.output_suffix)
        Matrix_functions.decomposeTransformWorldMatrixTo(pole_ik_joint, pole_output)
        MC.parentObject(pole_output, self.output_hierarchy)

        # Create IK end output
        end_output = MC.createTransform(self.getComponentFullPrefix() + "end" + MNRB_Names.output_suffix)
        Matrix_functions.decomposeTransformWorldMatrixTo(end_ik_joint, end_output)
        MC.parentObject(end_output, self.output_hierarchy)

        self.deform_outputs = [base_output, pole_output, end_output]

        # IK Creation
        ik_objects = MC.createRotatePlaneIkSolver(
            self.getComponentFullPrefix(),
            [base_ik_joint, pole_ik_joint, end_ik_joint])                       # Create IK
        
        # Create Pole Vector
        MC.createPoleVectorConstraint(
            pole_control.name,
            ik_objects[0],
            self.getComponentFullPrefix() + "simple_rps_poleVectorConstraint")
    
        # Constraint Base and end
        Ik_end_anchor = MC.createTransform(end_control.name + "_ik_anchor")
        MC.parentObject(Ik_end_anchor, ik_system_hierarchy)
        Matrix_functions.setMatrixParentNoOffset(Ik_end_anchor, end_control.name)

        MC.parentObject(ik_objects[0], Ik_end_anchor)

        Matrix_functions.setMatrixParentNoOffset(base_ik_joint, base_control.name)
        MC.createOrientConstraint(end_control.name, end_ik_joint)

        return True

    def connectComponent(self):
        '''
        Component Function that takes all the input connections from other components and connects them into the component structure
        '''
        if not super().connectComponent():
            return False

        # Get Name of base srt input parent
        base_srt_parent = self.getInputConnectionValueAt(0)
        if base_srt_parent == None:
            return False
        
        base_srt_parent_name = base_srt_parent + MNRB_Names.output_suffix

        base_parent_offset_compose_node, base_parent_offset_mult_matrix_node = Matrix_functions.setMatrixParentWithOffset(self.base_input, base_srt_parent_name)

        # Get Name of second input socket (connected deform srt name)
        deform_parent_name = self.getInputConnectionValueAt(1)
        if deform_parent_name == None:
            return False
        deform_parent = deform_parent_name + MNRB_Names.deform_suffix

        # Connect deform part of the component
        MC.parentObject(self.deforms[0].name, deform_parent)

        Matrix_functions.setLiveMatrixParentNoOffset(self.deforms[0].name, self.deform_outputs[0], deform_parent)
        Matrix_functions.setLiveMatrixParentNoOffset(self.deforms[1].name, self.deform_outputs[1], self.deforms[0].name)
        Matrix_functions.setLiveMatrixParentNoOffset(self.deforms[2].name, self.deform_outputs[2], self.deforms[1].name)
        
        # Get Name of ik srt input parent
        ik_srt_parent = self.getInputConnectionValueAt(2)
        if ik_srt_parent == None:
            return False
        
        ik_srt_parent_name = ik_srt_parent + MNRB_Names.output_suffix

        pole_parent_offset_compose_node, pole_parent_offset_mult_matrix_node = Matrix_functions.setMatrixParentWithOffset(self.pole_input, ik_srt_parent_name)
        end_parent_offset_compose_node, end_parent_offset_mult_matrix_node = Matrix_functions.setMatrixParentWithOffset(self.end_input, ik_srt_parent_name)

        return True

    def calculate_pole_vector_position(self, start_matrix, mid_matrix, end_matrix, multiplier=1.0):
        """
        Calculate pole vector position for a 3-joint IK chain.
        
        Args:
            start_pos: tuple/list (x, y, z) - start joint position
            mid_pos: tuple/list (x, y, z) - middle joint position
            end_pos: tuple/list (x, y, z) - end joint position
            multiplier: float - distance multiplier to push pole vector out
        
        Returns:
            tuple: (x, y, z) pole vector position
        """
        start_pos = [start_matrix[12], start_matrix[13], start_matrix[14]]
        mid_pos = [mid_matrix[12], mid_matrix[13], mid_matrix[14]]
        end_pos = [end_matrix[12], end_matrix[13], end_matrix[14]]
        
        # Find the midpoint between start and end
        chain_mid = [
            (start_pos[0] + end_pos[0]) / 2.0,
            (start_pos[1] + end_pos[1]) / 2.0,
            (start_pos[2] + end_pos[2]) / 2.0
        ]
        
        # Vector from chain midpoint to the actual middle joint
        pole_direction = [
            mid_pos[0] - chain_mid[0],
            mid_pos[1] - chain_mid[1],
            mid_pos[2] - chain_mid[2]
        ]
        
        # Calculate magnitude (length) of the vector
        magnitude = math.sqrt(
            pole_direction[0]**2 + 
            pole_direction[1]**2 + 
            pole_direction[2]**2
        )
        
        # Normalize the vector (make it unit length)
        if magnitude > 0:
            pole_direction = [
                pole_direction[0] / magnitude,
                pole_direction[1] / magnitude,
                pole_direction[2] / magnitude
            ]
        
        # Scale by multiplier
        pole_direction = [
            pole_direction[0] * multiplier,
            pole_direction[1] * multiplier,
            pole_direction[2] * multiplier
        ]
        
        # Final pole vector position
        pole_pos = [
            mid_pos[0] + pole_direction[0],
            mid_pos[1] + pole_direction[1],
            mid_pos[2] + pole_direction[2]
        ]
        
        return tuple(pole_pos)
