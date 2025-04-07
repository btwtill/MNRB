from collections import OrderedDict
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_Colors.colors import MNRBColor #type: ignore

CLASS_DEBUG = True

class NurbsShereOrientGuideShape(Serializable):
    def __init__(self, guide) -> None:
        super().__init__()
        self.guide = guide

        self.name = self.guide.name + MNRB_Names.guide_orient_suffix
        self.guide_material = None
        self.guide_shader = None

        self.nodes = []

    def draw(self):
        if CLASS_DEBUG: print("%s::draw::OrientShape Name::" % self.__class__.__name__, self.name)
        guide_shape = MC.createTransform(self.name)
        if CLASS_DEBUG: print("%s::draw::OrientShape Name::After Creation::" % self.__class__.__name__, guide_shape)

        self.name = guide_shape

        #create Shape of the orientation object

        direction_X_object = MC.createNurbsCone(self.name + MNRB_Names.guide_orient_suffix  + "_X", axis = [1, 0, 0], radius = 0.5)
        direction_X_shape_node = MC.getHierarchyContent(direction_X_object)[0]
        MC.setAttribute(direction_X_object, "translateX", 2)
        MC.applyTransform(direction_X_object)
        MC.parentShape(direction_X_shape_node, self.name)
        MC.deleteNode(direction_X_object)
        MC.assignObjectToShaderSet(direction_X_shape_node, MNRBColor.red.name + MNRB_Names.guide_shader_suffix)

        direction_Y_object = MC.createNurbsCone(self.name + MNRB_Names.guide_orient_suffix  + "_Y", axis = [0, 1, 0], radius = 0.5)
        direction_Y_shape_node = MC.getHierarchyContent(direction_Y_object)[0]
        MC.setAttribute(direction_Y_object, "translateY", 2)
        MC.applyTransform(direction_Y_object)
        MC.parentShape(direction_Y_shape_node, self.name)
        MC.deleteNode(direction_Y_object)
        MC.assignObjectToShaderSet(direction_Y_shape_node, MNRBColor.green.name + MNRB_Names.guide_shader_suffix)

        direction_Z_object = MC.createNurbsCone(self.name + MNRB_Names.guide_orient_suffix  + "_Z", axis = [0, 0, 1], radius = 0.5)
        direction_Z_shape_node = MC.getHierarchyContent(direction_Z_object)[0]
        MC.setAttribute(direction_Z_object, "translateZ", 2)
        MC.applyTransform(direction_Z_object)
        MC.parentShape(direction_Z_shape_node, self.name)
        MC.deleteNode(direction_Z_object)
        MC.assignObjectToShaderSet(direction_Z_shape_node, MNRBColor.blue.name + MNRB_Names.guide_shader_suffix)

        MC.parentObject(self.name, self.guide.node.guide_visualization_hierarchy)

        MC.connectAttribute(self.guide.name, "worldMatrix[0]", self.name, "offsetParentMatrix")
        MC.setDisplayType(self.name, "reference")

        self.hide()

    def resize(self, size):
        MC.setAttributeDouble3(self.name, "scale", size, size, size)

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
                print("%s::updateName::To " % self.__class__.__name__, new_name + MNRB_Names.guide_orient_suffix)
            old_name = self.name
            self.name = MC.renameObject(self.name, new_name + MNRB_Names.guide_orient_suffix)

            for index, node in enumerate(self.nodes):
                if CLASS_DEBUG: 
                    print("%s::updateName::Update Name of Node: " % self.__class__.__name__, node, " at index: ", index)
                    print("%s::updateName:: \t Try replacing: " % self.__class__.__name__, old_name, " with: ", new_name + MNRB_Names.guide_orient_suffix)
                    print("%s::updateName:: \t New Name: " % self.__class__.__name__, node.replace(old_name, new_name + MNRB_Names.guide_orient_suffix))
                new_node_name = node.replace(old_name, new_name + MNRB_Names.guide_orient_suffix)
                self.nodes[index] = MC.renameObject(node, new_node_name)

    def updateColor(self):
        if MC.objectExists(self.name):
            shape_node = MC.getHierarchyContent(self.name)[0]
            MC.assignObjectToShaderSet(shape_node, self.guide.color.name + MNRB_Names.guide_shader_suffix)

    def hide(self):
        MC.setAttribute(self.name, "visibility", False)

    def show(self):
        MC.setAttribute(self.name, "visibility", True)

    def serialize(self):
        if CLASS_DEBUG: print("%s::serialize::" % self.__class__.__name__)
        result_data = OrderedDict([('id', self.id),
                                  ('name', self.name),
                                  ('guide_orient_nodes', self.nodes)])
        return result_data
    
    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.id = data['id']

        self.name = data['name']

        for node in data['guide_orient_nodes']:
            self.nodes.append(node)