from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore

class NurbsShereGuideShape():
    def __init__(self, guide) -> None:
        self.guide = guide

        self.guide_material = None
        self.guide_shader = None

    def draw(self):
        guide_shape = MC.createNurbsSphere(self.guide.name)
        self.guide.name = guide_shape
        MC.assignObjectToShaderSet(guide_shape, self.guide.color.name + MNRB_Names.guide_shader_suffix)

    def resize(self, size):
        MC.setNurbsSphereShapeRadius(self.guide.name, size)

    def updateColor(self):
        if MC.objectExists(self.guide.name):
            shape_node = MC.getHierarchyContent(self.guide.name)[0]
            MC.assignObjectToShaderSet(shape_node, self.guide.color.name + MNRB_Names.guide_shader_suffix)