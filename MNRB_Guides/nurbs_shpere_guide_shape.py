from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.global_variables import GUIDE_SHADER_SUFFIX #type: ignore

class NurbsShereGuideShape():
    def __init__(self, guide) -> None:
        self.guide = guide

        self.guide_material = None
        self.guide_shader = None

    def draw(self):
        guide_shape = MC.createNurbsSphere(self.guide.name)
        self.guide.name = guide_shape
        MC.assignObjectToShaderSet(guide_shape, self.guide.color.name + GUIDE_SHADER_SUFFIX)

    def resize(self, size):
        MC.setNurbsSphereShapeRadius(self.guide.name, size)

    def updateColor(self):
        pass