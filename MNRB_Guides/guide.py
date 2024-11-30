from enum import Enum
from collections import OrderedDict
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_Guides.locator_guide_shape import LocatorGuideShape #type: ignore
from MNRB.MNRB_Guides.nurbs_shpere_guide_shape import NurbsShereGuideShape #type: ignore
from MNRB.MNRB_colors.colors import MNRBColor #type: ignore
from MNRB.global_variables import GUIDE_SUFFIX #type: ignore

CLASS_DEBUG = True

class guideShapeType(Enum):
    locator = 1
    sphere = 2

class guide(Serializable):
    def __init__(self, node, name, position = (0, 0, 0), deserialized = False) -> None:
        super().__init__()

        self.node = node

        self._guide_type = guideShapeType.locator

        if not deserialized:
            self.name = self.node.properties.component_name + "_" + name + GUIDE_SUFFIX
        else:
            self.name = name

        self._color = self.node.component_color

        self.position = position
        self.size = self.node.properties.guide_size

        self.guide_shape = self.createGuideShape()

        if not deserialized:
            self.draw()

        if not deserialized:
            self.node.guides.append(self)

    @property
    def guide_type(self): return self._guide_type
    @guide_type.setter
    def guide_type(self, value):
        self._guide_type = value

        self.guide_shape = self.createGuideShape()

    @property
    def color(self): return self._color
    @color.setter
    def color(self, value):
        if self._color != value:
            self._color = value
            if CLASS_DEBUG: print("%s:: --component_color:: Setting new Guide Color:: " % self.__class__.__name__, self.color)
            self.setColor()

        self._color = value

    def draw(self):
        self.guide_shape.draw()
        self.guide_shape.resize(self.size)

    def resize(self, size):
        self.guide_shape.resize(size)

    def setColor(self):
        self.guide_shape.updateColor()

    def determinGuideShape(self):
        print("GUIDE:: --determinGuideShape:: guide Type: ", self.guide_type)
        if self.guide_type.value == guideShapeType.locator.value:
            print("GUIDE:: --determinGuideShape::  Return Value:: ", LocatorGuideShape)
            return LocatorGuideShape
        if self.guide_type.value == guideShapeType.sphere.value:
            return NurbsShereGuideShape

    def createGuideShape(self):
        self.guide_shape = self.determinGuideShape()(self)
        return self.guide_shape

    def updateName(self, name):
        if MC.objectExists(self.name):
            if CLASS_DEBUG: print("%s:: --updateName:: Setting Guide name to:: " % self.__class__.__name__, name)
            original_name_ending_list = self.name.split("_")
            remaining_name = "_".join(original_name_ending_list[1:])
            if CLASS_DEBUG: print("%s:: --updateName:: old Remaining Name:: " % self.__class__.__name__, remaining_name)
            new_name = name + "_" + remaining_name
            if CLASS_DEBUG: print("%s:: --updateName:: Final Guide Name to Rename:: " % self.__class__.__name__, new_name)
            self.name = MC.renameObject(self.name, new_name)

    def serialize(self):
        serialized_data = OrderedDict([
            ('id', self.id),
            ('name', self.name)
        ])
        return serialized_data

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.id = data['id']
        return True