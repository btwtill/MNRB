import json
import os
from collections import OrderedDict
from MNRB.ROSE_Data.rose_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Controls.control_shape import control_shape #type: ignore

class control(Serializable):
    def __init__(self, node, name = "", control_type = 0, deserialized = False):
        super().__init__()

        self.node = node
        self.node.controls.append(self)
         
        self.control_name  = name
        self.name = self.assembleFullName()

        self._control_type = control_type
        self.shape_path = self.determinShapePath()
        self.control_shape = control_shape(self)

        if not deserialized:
            self.draw()

    @property
    def control_type(self): return self._control_type
    @control_type.setter
    def control_type(self, value):
        self._control_type = value

        self.shape_path = self.determinShapePath()

    def assembleFullName(self):
        return self.node.getComponentPrefix() + self.node.getComponentName() + "_" + self.control_name + MNRB_Names.control_suffix

    def draw(self):
        self.control_shape.draw()

    def exists(self):
        return MC.objectExists(self.name)

    def updateColor(self, color):
        self.control_shape.updateColor(color.value)

    def select(self):
        MC.selectObject(self.name)

    def determinShapePath(self):
        control_shape_dict = self.loadControlShapes()

        return control_shape_dict['shapes'][self.control_type]['path']

    def loadControlShapes(self):
        path = os.path.join(os.path.dirname(__file__), "control_shapes.json")
        with open(path, "r") as file:
            raw_data = file.read()
            data = json.loads(raw_data)
        
        return data

    def setPosition(self, matrix):
        MC.setObjectWorldPositionMatrix(self.name, matrix)
        MC.applyTransformScale(self.name)

    def setScale(self, scale):
        MC.scaleTransform(self.name, [scale, scale, scale])
        MC.applyTransformScale(self.name)

    def serialize(self):
        serialized_data = OrderedDict([
            ('id', self.id),
            ('control_name', self.control_name),
            ('control_type', self.control_type)
        ])
        return serialized_data
    
    def deserialize(self, data, hashmap = {}, restore_id = True):
        if restore_id: self.id = data['id']

        self.control_name = data['control_name']
        self.control_type = data['control_type']

        self.name = self.assembleFullName()

        return True
