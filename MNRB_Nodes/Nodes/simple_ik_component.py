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

GUIDE_DEBUG = True

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
        return super().componentBuild()

    def connectComponent(self):
        return super().connectComponent()