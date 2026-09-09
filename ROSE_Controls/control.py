import hashlib
import json
import os
from collections import OrderedDict
from MNRB.ROSE_Data.rose_Editor_Serializable import Serializable #type: ignore
from MNRB.ROSE_naming.ROSE_names import ROSE_Names #type: ignore
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.ROSE_Controls.control_shape import control_shape #type: ignore

class control(Serializable):
    def __init__(self, node, name = "", control_type = 0, deserialized = False):
        super().__init__()

        self.node = node
        self.node.controls.append(self)
         
        self.control_name  = name
        self.id = self.assembleStableId()
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
        return self.node.getComponentPrefix() + self.node.getComponentName() + "_" + self.control_name + ROSE_Names.control_suffix

    def assembleStableId(self):
        #derived, not generated - same reasoning as deform.assembleStableId().
        #componentBuild drops every control and recreates it, so a generated id
        #would change on every build, and anything holding a reference to a
        #control (the Attribute Editor's control-to-attribute assignments) would
        #lose it. control_name is the slot ("base", "pole", "chain_2") - unique
        #within a node and unaffected by renaming the component, unlike self.name.
        key = "%s:%s" % (self.node.id, self.control_name)
        return int.from_bytes(hashlib.sha1(key.encode()).digest()[:8], "big") >> 1

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
        self.control_name = data['control_name']
        self.control_type = data['control_type']

        #stored id ignored on purpose: this id is derived, so recomputing it keeps
        #a project saved before this change from losing its control references
        self.id = self.assembleStableId()
        self.name = self.assembleFullName()

        return True
