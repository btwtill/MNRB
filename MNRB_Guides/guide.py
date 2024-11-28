from enum import Enum
from collections import OrderedDict
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_Guides.locator_guide_shape import LocatorGuideShape #type: ignore
from MNRB.MNRB_Guides.nurbs_shpere_guide_shape import NurbsShereGuideShape #type: ignore

class guideShapeType(Enum):
    locator = 1
    sphere = 2

class guide(Serializable):
    def __init__(self, node, name, color = (1, 1, 0), position = (0, 0, 0), size = 1, guide_type = guideShapeType.locator) -> None:
        super().__init__()
        
        self.node = node

        self._guide_type = guide_type

        self.name = name
        self._color = color

        self.position = position
        self.size = 1

        self.guide_shape = self.createGuideShape()

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
            self.setColor()

        self._color = value

    def draw(self):
        self.guide_shape.draw()

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

    def serialize(self):
        serialized_data = OrderedDict([
            ('id', self.id),
            ('name', self.name)
        ])
        return serialized_data

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.id = data['id']
        return True