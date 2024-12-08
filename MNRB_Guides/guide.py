from enum import Enum
from collections import OrderedDict
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_Guides.locator_guide_shape import LocatorGuideShape #type: ignore
from MNRB.MNRB_Guides.nurbs_shpere_guide_shape import NurbsShereGuideShape #type: ignore
from MNRB.MNRB_naming.MNRB_names import MNRB_Names #type: ignore

CLASS_DEBUG = True

class guideShapeType(Enum):
    locator = 1
    sphere = 2

class guide(Serializable):
    def __init__(self, node, name = "", position = (0, 0, 0), deserialized = False) -> None:
        super().__init__()

        self.node = node

        self._guide_type = guideShapeType.sphere

        self.guide_name = name
        self.name = self.assembleFullName()
        
        self._color = self.node.properties.component_color

        self.position = position
        self.size = self.node.properties.guide_size

        self.guide_shape = self.createGuideShape()

        self.node.guides.append(self)

        if not deserialized:
            self.draw()

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

    def exists(self) -> bool:
        return MC.objectExists(self.name)

    def getPosition(self):
        return MC.getObjectWorldPositionMatrix(self.name)

    def setColor(self):
        self.guide_shape.updateColor()

    def setPosition(self, matrix):
        MC.setObjectWorldPositionMatrix(self.name, matrix)

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

    def assembleFullName(self):
        return self.node.getComponentPrefix() + self.node.getComponentName() + "_" + self.guide_name + MNRB_Names.guide_suffix

    def updateName(self, has_duplicate_name):
        if self.exists():
            if CLASS_DEBUG: print("%s:: --updateName:: Old Guide Name:: " % self.__class__.__name__, self.name)
            new_name =  self.assembleFullName()
            if CLASS_DEBUG: print("%s:: --updateName:: new Guide Name:: " % self.__class__.__name__, new_name)

            if new_name == self.name:
                return

            if has_duplicate_name:
                duplicate_name = MC.findDuplicatesInNodeHiearchyByName(self.node.scene.virtual_rig_hierarchy.guide_hierarchy_object.name, new_name)
                if CLASS_DEBUG: print("%s:: --updateName:: Duplicate:: " % self.__class__.__name__, duplicate_name)
                if duplicate_name != []:
                    new_name = new_name + str(duplicate_name[1])
            if CLASS_DEBUG: print("%s:: --updateName:: Final Guide Name to Rename:: " % self.__class__.__name__, new_name)
            self.name = MC.renameObject(self.name, new_name)

    def serialize(self):
        serialized_data = OrderedDict([
            ('id', self.id),
            ('name', self.guide_name),
        ])
        return serialized_data

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.id = data['id']
        self.guide_name = data['name']

        self.assembleFullName()

        return True