import os
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

class control_shape():
    def __init__(self, control):
        self.control = control
        self.default_namespace = "import"
        self.base_path = os.path.dirname(__file__)

    def draw(self):
        #import shape
        MC.importBinaryFile(os.path.join(self.base_path, self.control.shape_path), namespace = self.default_namespace)
        imported_objects = MC.selectNamespace(self.default_namespace)

        imported_control = imported_objects[0]

        imported_control_name_parts = imported_control.split(":")
        imported_control_name = imported_control_name_parts[1]

        MC.mergeNamespaceWithRoot(self.default_namespace)
        self.control.name = MC.renameObject(imported_control_name, self.control.name)

        self.updateColor(self.control.node.properties.component_color.value)

        MC.scaleTransform(self.control.name, [self.control.node.properties.control_size, self.control.node.properties.control_size, self.control.node.properties.control_size])
        MC.applyTransformScale(self.control.name)

    def updateColor(self, color):
        all_shapes = MC.getObjectShapeNodes(self.control.name)

        for shape in all_shapes:
            MC.setShapeNodeColor(shape, color)