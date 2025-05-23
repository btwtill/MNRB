from enum import Enum
from collections import OrderedDict
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_Guides.MNRB_Guide_Shapes.locator_guide_shape import LocatorGuideShape #type: ignore
from MNRB.MNRB_Guides.MNRB_Guide_Shapes.nurbs_shpere_guide_shape import NurbsShereGuideShape #type: ignore
from MNRB.MNRB_Guides.MNRB_Up_Shapes.nurbs_up_guide_shape import NurbsShereUpGuideShape #type:ignore
from MNRB.MNRB_Guides.MNRB_Up_Shapes.locator_up_guide_shape import LocatorUpGuideShape #type:ignore
from MNRB.MNRB_Guides.MNRB_Orientation_Shapes.nurbs_orient_guide_shape import NurbsShereOrientGuideShape #type:ignore
from MNRB.MNRB_Guides.MNRB_Orientation_Shapes.locator_orient_guide_shape import LocatorOrientGuideShape #type:ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore
from MNRB.MNRB_cmds_wrapper.matrix_functions import Matrix_functions #type: ignore
from MNRB.MNRB_Guides.MNRB_Guide_Connector.guide_connector import Guide_Connector #type: ignore

CLASS_DEBUG = True

class guideShapeType(Enum):
    locator = 1
    sphere = 2

class guide(Serializable):
    def __init__(self, node, name = "", guide_parent = None, position = (0, 0, 0), deserialized = False) -> None:
        super().__init__()

        self.node = node
        self._guide_parent = None
        self.parent_connector = None

        self._guide_type = guideShapeType.sphere
        self.orientation_object_display = False

        self.guide_name = name
        self.name = self.assembleFullName()
        
        self._color = self.node.properties.component_color

        self.position = position
        self.size = self.node.properties.guide_size

        self.guide_shape = self.createGuideShape()
        self.guide_up_shape = self.createGuideUpShape()
        self.guide_orientation_shape = self.createGuideOrientationShape()

        self.node.guides.append(self)

        if not deserialized:
            self.draw()
        
        self.guide_parent = guide_parent

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

    @property
    def guide_parent(self): return self._guide_parent
    @guide_parent.setter
    def guide_parent(self, value):
        if CLASS_DEBUG: print("%s::guide_parent::setter to: " % self.__class__.__name__, value)
        if self.parent_connector is not None:
            self.parent_connector.update()
        elif self.parent_connector == None and value != None:
            if CLASS_DEBUG: print("%s::guide_parent::setter: " % self.__class__.__name__, self.parent_connector)
            if CLASS_DEBUG: print("%s::guide_parent::setter: " % self.__class__.__name__, self._guide_parent," ::trying to set to value:: ", value)
            self.parent_connector = Guide_Connector(value, self)
            self._guide_parent = value
            self.parent_connector.build()
        else:
            self._guide_parent = value

    def draw(self):
        self.guide_shape.draw()
        self.guide_shape.resize(self.size)

        self.guide_up_shape.draw()
        self.guide_up_shape.resize(self.size)

        self.guide_orientation_shape.draw()
        self.guide_orientation_shape.resize(self.size)

    def resize(self, size):
        self.guide_shape.resize(size)
        self.guide_up_shape.resize(size)
        self.guide_orientation_shape.resize(size)

    def exists(self) -> bool:
        return MC.objectExists(self.name)

    def getPosition(self, reset_scale = True):
        guide_pos = MC.getObjectWorldPositionMatrix(self.guide_orientation_shape.name)
        if not reset_scale:
            return guide_pos
        guide_noScale_pos = Matrix_functions.removeScaleFromMatrix(guide_pos)
        return guide_noScale_pos

    def setColor(self):
        self.guide_shape.updateColor()
        self.guide_up_shape.updateColor()
        if self.parent_connector is not None:
                self.parent_connector.updateColor()

    def setPosition(self, matrix):
        MC.setObjectWorldPositionMatrix(self.name, matrix)

    def select(self):
        if self.exists():
            MC.selectObject(self.name)

    def determinGuideShape(self):
        if CLASS_DEBUG: print("GUIDE:: --determinGuideShape:: guide Type: ", self.guide_type)
        if self.guide_type.value == guideShapeType.locator.value:
            if CLASS_DEBUG: print("GUIDE:: --determinGuideShape::  Return Value:: ", LocatorGuideShape)
            return LocatorGuideShape
        if self.guide_type.value == guideShapeType.sphere.value:
            if CLASS_DEBUG: print("GUIDE:: --determinGuideShape::  Return Value:: ", NurbsShereGuideShape)
            return NurbsShereGuideShape

    def determinGuideUpShape(self):
        if CLASS_DEBUG: print("GUIDE:: --determinGuideUpShape:: guide Type: ", self.guide_type)
        if self.guide_type.value == guideShapeType.locator.value:
            if CLASS_DEBUG: print("GUIDE:: --determinGuideUpShape::  Return Value:: ", LocatorGuideShape)
            return LocatorUpGuideShape
        if self.guide_type.value == guideShapeType.sphere.value:
            if CLASS_DEBUG: print("GUIDE:: --determinGuideShape::  Return Value:: ", NurbsShereUpGuideShape)
            return NurbsShereUpGuideShape
    
    def determinGuideOrientationShape(self):
        if CLASS_DEBUG: print("GUIDE:: --determinGuideOrientationShape:: guide Type: ", self.guide_type)
        if self.guide_type.value == guideShapeType.locator.value:
            if CLASS_DEBUG: print("GUIDE:: --determinGuideOrientationShape::  Return Value:: ", LocatorGuideShape)
            return LocatorOrientGuideShape
        if self.guide_type.value == guideShapeType.sphere.value:
            if CLASS_DEBUG: print("GUIDE:: --determinGuideShape::  Return Value:: ", NurbsShereOrientGuideShape)
            return NurbsShereOrientGuideShape

    def createGuideShape(self):
        self.guide_shape = self.determinGuideShape()(self)
        return self.guide_shape

    def createGuideUpShape(self):
        if CLASS_DEBUG: print("%s::createGuideOrientationShape:: " % self.__class__.__name__)
        self.guide_up_shape = self.determinGuideUpShape()(self)
        return self.guide_up_shape

    def createGuideOrientationShape(self):
        if CLASS_DEBUG: print("%s::createGuideUpShape:: " % self.__class__.__name__)
        self.guide_orientation_shape = self.determinGuideOrientationShape()(self)
        return self.guide_orientation_shape

    def assembleFullName(self):
        return self.node.getComponentPrefix() + self.node.getComponentName() + "_" + self.guide_name + MNRB_Names.guide_suffix

    def setOrientationShapeDisplay(self, value):
        if self.exists():
            if value:
                self.guide_orientation_shape.show()
            else:
                self.guide_orientation_shape.hide()

    def setExtendedRotationControlDisplay(self, value):
        if self.exists():
            if value:
                self.guide_up_shape.show()
            else:
                self.guide_up_shape.hide()

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
            
            if CLASS_DEBUG: print("%s::updateName::About to update orientShape and upShape::" % self.__class__.__name__)

            self.guide_orientation_shape.updateName(new_name)
            self.guide_up_shape.updateName(new_name)

            if CLASS_DEBUG: print("%s::updateName::parent_connector::" % self.__class__.__name__, self.parent_connector)

            if self.parent_connector is not None:
                if CLASS_DEBUG: print("%s::updateName::About to update connector::" % self.__class__.__name__)
                self.parent_connector.updateName(new_name)

    def remove(self):
        if self.exists():
            MC.deleteNode(self.name)
        if self.guide_up_shape.exists():
            self.guide_up_shape.remove()
        if self.guide_orientation_shape.exists():
            self.guide_orientation_shape.remove()
        if self.parent_connector != None:
            self.parent_connector.remove()

    def parentToGuide(self):
        if CLASS_DEBUG: print("%s::parentToGuide::" % self.__class__.__name__)

    def serialize(self):

        serialized_data = OrderedDict([
            ('id', self.id),
            ('name', self.guide_name),
            ('guide_parent_id', self.guide_parent.id if self.guide_parent is not None else None),
            ('connector_id', self.parent_connector.id if self.parent_connector is not None else None),
            ('up_shape', self.guide_up_shape.serialize()),
            ('orientation_shape', self.guide_orientation_shape.serialize())
        ])
        return serialized_data

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.id = data['id']
        self.guide_name = data['name']
 
        self.name = self.assembleFullName()
        
        if data['orientation_shape'] is not None:
            self.guide_orientation_shape.deserialize(data['orientation_shape'], hashmap, restore_id)

        if data['up_shape'] is not None:
            self.guide_up_shape.deserialize(data['up_shape'], hashmap, restore_id)

        if data['guide_parent_id'] is not None:
            hashmap[self.id] = data['guide_parent_id']

        if CLASS_DEBUG: 
            print("%s::deserialize:: Guide Name:: " % self.__class__.__name__, self.guide_up_shape.name)
            print("%s::deserialize:: Guide Orient Name:: " % self.__class__.__name__, self.guide_orientation_shape.name)

        return True