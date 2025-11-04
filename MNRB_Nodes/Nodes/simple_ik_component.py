from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_Node #type: ignore
from MNRB.MNRB_Colors.colors import MNRBColor #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_template import MNRB_NodeTemplate #type: ignore
from MNRB.MNRB_Nodes.node_Editor_conf import OPERATIONCODE_SIMPLEIKCOMPONENT, registerNode #type: ignore
from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_NodeProperties #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket import NodeEditor_Socket #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.MNRB_Guides.guide import guide #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

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
        '''

        if not super().guideBuild():    # Check if the basic guide Strucutre is successfully build and only then continue
            return False
        
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
    
    def staticBuild(self):
        return super().staticBuild()

    def componentBuild(self):
        return super().componentBuild()

    def connectComponent(self):
        return super().connectComponent()