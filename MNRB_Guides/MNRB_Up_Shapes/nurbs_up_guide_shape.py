from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore

CLASS_DEBUG = True

class NurbsShereUpGuideShape():
    def __init__(self, guide) -> None:
        self.guide = guide

        self.offset_node = None

        self.guide_material = None
        self.guide_shader = None

    def draw(self):
        if CLASS_DEBUG: print("%s::draw::UpShape Name::" % self.__class__.__name__, self.guide.name_up)
        guide_shape = MC.createNurbsSphere(self.guide.name_up)
        if CLASS_DEBUG: print("%s::draw::UpShape Name::After Creation::" % self.__class__.__name__, guide_shape)
        self.guide.name_up = guide_shape
        MC.assignObjectToShaderSet(guide_shape, self.guide.color.name + MNRB_Names.guide_shader_suffix)

        #create nodes to position and connect correctly
        self.offset_node = MC.createComposeNode(self.guide.name_up + "_offset")
        MC.setAttribute(self.offset_node, "inputTranslateY", 2.0)
        
        offset_multiply_node = MC.createMultMatrixNode(self.guide.name_up + "_offset")
        MC.connectAttribute(self.offset_node, "outputMatrix", offset_multiply_node, "matrixIn[0]")
        MC.connectAttribute(self.guide.name, "worldMatrix[0]", offset_multiply_node, "matrixIn[1]")
        MC.connectAttribute(offset_multiply_node, "matrixSum", self.guide.name_up, "offsetParentMatrix")

        MC.parentObject(self.guide.name_up, self.guide.node.guide_visualization_hierarchy)

        self.show()

    def hide(self):
        MC.setOverrideVisibility(self.guide.name_up, False)

    def show(self):
        MC.setOverrideVisibility(self.guide.name_up, True)

    def resize(self, size):
        MC.setNurbsSphereShapeRadius(self.guide.name_up, size / 2)
        MC.setAttribute(self.guide.name_up + "_offset" + "_cm_fNode", "inputTranslateY", size + size)

    def updateName(self, new_name):
        if MC.objectExists(self.guide.name_up):
            if CLASS_DEBUG: 
                print("%s::updateName::" % self.__class__.__name__)
                print("%s::updateName::From " % self.__class__.__name__, self.guide.name_up)
                print("%s::updateName::To " % self.__class__.__name__, new_name + MNRB_Names.guide_up_suffix)
            self.guide.name_up = MC.renameObject(self.guide.name_up, new_name + MNRB_Names.guide_up_suffix)

    def updateColor(self):
        if MC.objectExists(self.guide.name_up):
            MC.assignObjectToShaderSet(self.guide.name_up, self.guide.color.name + MNRB_Names.guide_shader_suffix)