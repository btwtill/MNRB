from MNRB.ROSE_Nodes.rose_node_base import ROSE_Node #type: ignore
from MNRB.ROSE_colors.colors import ROSEColor #type: ignore

class ROSE_NodeTemplate(ROSE_Node):
    def __init__(self, scene, inputs=..., outputs=..., color=ROSEColor.yellow):
        super().__init__(scene, inputs, outputs, color)

    def guideBuild(self):
        return super().guideBuild()
    
    def staticBuild(self):
        return super().staticBuild()

    def componentBuild(self):
        return super().componentBuild()

    def connectComponent(self):
        return super().connectComponent()