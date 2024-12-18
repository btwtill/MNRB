from MNRB.MNRB_Nodes.mnrb_node_base import MNRB_Node #type: ignore
from MNRB.MNRB_Colors.colors import MNRBColor #type: ignore

class MNRB_NodeTemplate(MNRB_Node):
    def __init__(self, scene, inputs=..., outputs=..., color=MNRBColor.yellow):
        super().__init__(scene, inputs, outputs, color)

    def guideBuild(self):
        return super().guideBuild()
    
    def staticBuild(self):
        return super().staticBuild()

    def componentBuild(self):
        return super().componentBuild()

    def connectComponent(self):
        return super().connectComponent()