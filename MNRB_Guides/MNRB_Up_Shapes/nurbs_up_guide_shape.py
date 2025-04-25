from collections import OrderedDict
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore

CLASS_DEBUG = True

class NurbsShereUpGuideShape(Serializable):
    def __init__(self, guide) -> None:
        super().__init__()
        self.guide = guide

        self.name = self.guide.name + MNRB_Names.guide_up_suffix

        self.guide_material = None
        self.guide_shader = None

        self.nodes = []

    def draw(self):
        if CLASS_DEBUG: print("%s::draw::UpShape Name::" % self.__class__.__name__, self.name)
        guide_shape = MC.createNurbsSphere(self.name)

        MC.setNurbsSphereShapeDegree(guide_shape, 1)
        MC.setNurbsSphereShapeSections(guide_shape, 2)
        MC.setNurbsSphereShapeSpans(guide_shape, 2)

        if CLASS_DEBUG: print("%s::draw::UpShape Name::After Creation::" % self.__class__.__name__, guide_shape)
        self.name = guide_shape
        MC.assignObjectToShaderSet(guide_shape, self.guide.color.name + MNRB_Names.guide_shader_suffix)

        #create nodes to position and connect correctly
        self.offset_node = MC.createComposeNode(self.name + "_offset")
        self.nodes.append(self.offset_node)
        MC.setAttribute(self.offset_node, "inputTranslateY", 3.0)
        
        offset_multiply_node = MC.createMultMatrixNode(self.name + "_offset")
        self.nodes.append(offset_multiply_node)

        MC.connectAttribute(self.offset_node, "outputMatrix", offset_multiply_node, "matrixIn[0]")
        MC.connectAttribute(self.guide.name, "worldMatrix[0]", offset_multiply_node, "matrixIn[1]")
        MC.connectAttribute(offset_multiply_node, "matrixSum", self.name, "offsetParentMatrix")

        MC.parentObject(self.name, self.guide.node.guide_visualization_hierarchy)

        if self.guide.node.properties.display_extended_rotation_controls:
            self.show()
        else:
            self.hide()

    def hide(self):
        MC.setOverrideVisibility(self.name, False)

    def show(self):
        MC.setOverrideVisibility(self.name, True)

    def resize(self, size):
        MC.setNurbsSphereShapeRadius(self.name, size / 2)
        MC.setAttribute(self.name + "_offset" + "_cm_fNode", "inputTranslateY", 3.0 * size)

    def exists(self):
        return MC.objectExists(self.name)

    def remove(self):
        if self.exists():
            MC.deleteNode(self.name)

    def updateName(self, new_name):
        if MC.objectExists(self.name):
            if CLASS_DEBUG: 
                print("%s::updateName::" % self.__class__.__name__)
                print("%s::updateName::From " % self.__class__.__name__, self.name)
                print("%s::updateName::To " % self.__class__.__name__, new_name + MNRB_Names.guide_up_suffix)
            old_name = self.name
            self.name = MC.renameObject(self.name, new_name + MNRB_Names.guide_up_suffix)

            for index, node in enumerate(self.nodes):
                if CLASS_DEBUG: 
                    print("%s::updateName::Update Name of Node: " % self.__class__.__name__, node, " at index: ", index)
                    print("%s::updateName:: \t Try replacing: " % self.__class__.__name__, old_name, " with: ", new_name + MNRB_Names.guide_up_suffix)
                    print("%s::updateName:: \t New Name: " % self.__class__.__name__, node.replace(old_name, new_name + MNRB_Names.guide_up_suffix))
                new_node_name = node.replace(old_name, new_name + MNRB_Names.guide_up_suffix)
                self.nodes[index] = MC.renameObject(node, new_node_name)

    def updateColor(self):
        if MC.objectExists(self.name):
            MC.assignObjectToShaderSet(self.name, self.guide.color.name + MNRB_Names.guide_shader_suffix)

    def serialize(self):
        serialized_data = OrderedDict([
            ('id', self.id),
            ('name', self.name),
            ('guide_up_nodes', self.nodes)
        ])
        return serialized_data
    
    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.id = data['id']

        self.name = data['name']

        for node in data['guide_up_nodes']:
            self.nodes.append(node)
