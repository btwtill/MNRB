from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore

CLASS_DEBUG = True

class NurbsShereOrientGuideShape():
    def __init__(self, guide) -> None:
        self.guide = guide

        self.guide_material = None
        self.guide_shader = None

    def draw(self):
        if CLASS_DEBUG: print("%s::draw::OrientShape Name::" % self.__class__.__name__, self.guide.name_orient)
        guide_shape = MC.createNurbsSphere(self.guide.name_orient)
        if CLASS_DEBUG: print("%s::draw::OrientShape Name::After Creation::" % self.__class__.__name__, guide_shape)
        self.guide.name_orient = guide_shape
        MC.assignObjectToShaderSet(guide_shape, self.guide.color.name + MNRB_Names.guide_shader_suffix)

    def resize(self, size):
        MC.setNurbsSphereShapeRadius(self.guide.name_orient, size)

    def updateColor(self):
        if MC.objectExists(self.guide.name_orient):
            MC.assignObjectToShaderSet(self.guide.name_orient, self.guide.color.name + MNRB_Names.guide_shader_suffix)