from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_Node #type: ignore
from MNRB.MNRB_Colors.colors import MNRBColor #type: ignore

class MNRB_NodeTemplate(MNRB_Node):
    def __init__(self, scene, inputs=..., outputs=..., color=MNRBColor.yellow):
        super().__init__(scene, inputs, outputs, color)

    def guideBuild(self):
        if super().guideBuild():
            return True
        else:
            return False

    def staticBuild(self):
        rebuild_guides = not self.validateGuideBuild()
        if super().staticBuild(rebuild_guides = rebuild_guides):
            return True
        else:
            return False

    def componentBuild(self):
        rebuild_static = not self.validateStaticBuild()
        if super().componentBuild(rebuild_static = rebuild_static):
            return True
        else:
            return False

    def connectComponent(self):
        rebuild_component = not self.validateComponentBuild()
        if super().connectComponent(rebuild_component = rebuild_component):
            return True
        else:
            return False
            
    def validateGuideBuild(self):
        return False

    def validateStaticBuild(self):
        return False
    
    def validateComponentBuild(self):
        return False
