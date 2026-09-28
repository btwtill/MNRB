import os
import maya.cmds as cmds #type: ignore
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.ROSE_Controls import control_shape_library #type: ignore

class control_shape():
    def __init__(self, control):
        self.control = control
        self.base_path = os.path.dirname(__file__)

    def resolveShape(self):
        """(shape file, size) for this control: its library shape if the Control
        Shapes tab assigned one and shapes are enabled, the default otherwise -
        either way at the component's control size times any scale override."""
        library_path, scale = control_shape_library.resolveControlShape(self.control.id)
        path = library_path or os.path.join(self.base_path, self.control.shape_path)
        return path, self.control.node.properties.control_size * scale

    def draw(self):
        path, size = self.resolveShape()

        #picks the curve object out of the file by type rather than taking
        #whichever node the import listed first
        self.control.name = control_shape_library.importShape(path, self.control.name)

        self.updateColor(self.control.node.properties.component_color.value)

        MC.scaleTransform(self.control.name, [size, size, size])
        MC.applyTransformScale(self.control.name)

        MC.deleteNodeHistory(self.control.name)

    def redraw(self):
        """Swap the shape of an already built control for what it resolves to now,
        leaving the control transform - and everything wired to it - as it is.

        A scale a component baked in after drawing (setScale) is not carried over:
        the new shape is drawn at the resolved size."""
        if not self.control.exists():
            return False

        path, size = self.resolveShape()
        control_shape_library.replaceControlShapes(self.control.name, path, size)
        self.updateColor(self.control.node.properties.component_color.value)
        return True

    def updateColor(self, color):
        if self.control.exists():
            #full paths: a short shape name can be shared by another object
            for shape in cmds.listRelatives(self.control.name, shapes = True, fullPath = True) or []:
                MC.setShapeNodeColor(shape, color)
