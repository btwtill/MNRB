from collections import OrderedDict
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Scene.scene_object import HierarchyObject #type: ignore
from MNRB.global_variables import GUIDE_HIERARCHY_SUFFIX, RIG_HIERARCHY_SUFFIX, RIG_HIERARCHY_COMPONENT_SUFFIX, RIG_HIERARCHY_SKELETON_SUFFIX, RIG_HIERARCHY_GEOMETRY_SUFFIX, RIG_HIERARCHY_SHAPES_SUFFIX #type: ignore

CLASS_DEBUG = True

class MNRB_Scene_Hierarchy():
    def __init__(self, scene) -> None:
        super().__init__()

        self.scene = scene

        self._hierarchy_name = self.scene.getSceneRigName()

        self.guide_hierarchy_suffix = GUIDE_HIERARCHY_SUFFIX
        self.rig_hierarchy_suffix = RIG_HIERARCHY_SUFFIX
        self.components_hiearchy_suffix = RIG_HIERARCHY_COMPONENT_SUFFIX
        self.skeleton_hiearchy_suffix = RIG_HIERARCHY_SKELETON_SUFFIX
        self.geometry_hiearchy_suffix = RIG_HIERARCHY_GEOMETRY_SUFFIX
        self.shapes_hiearchy_suffix = RIG_HIERARCHY_SHAPES_SUFFIX

        self.guide_hierarchy_object = None
        self.rig_hierarchy_object = None

        self._hierarchy_name_changed_listeners = []

        self.scene.properties.connectHasBeenModifiedCallback(self.updateGuideHierarchyName)

    @property
    def hierarchy_name(self): return self._hierarchy_name
    @hierarchy_name.setter
    def hierarchy_name(self, value):
        self._hierarchy_name = value

        for callback in self._hierarchy_name_changed_listeners: callback()

    def connectCallbackToHierarchyHasChanged(self, callback):
        self._hierarchy_name_changed_listeners.append(callback)

    def createGuideHierarchy(self):
        if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --createGuideHierarchy:: self.guide_hierarchy_object:: ", self.guide_hierarchy_object)
        self.guide_hierarchy_object = HierarchyObject(self, suffix = self.guide_hierarchy_suffix)

    def isGuideHierarchyObject(self) -> bool:
        if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --isGuideHierarchy:: self.guide_hierarchy_object:: ", self.guide_hierarchy_object)
        return False if self.guide_hierarchy_object is None else True

    def isGuideHierarchyInViewport(self) -> bool:
        if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --isGuideHierarchyInViewport:: Guide Hierarchy is in Maya viewport:: ", MC.objectExists(self.hierarchy_name + self.guide_hierarchy_suffix))
        return MC.objectExists(self.hierarchy_name + self.guide_hierarchy_suffix)
    
    def ensureGuideHierarchy(self):
        if self.isGuideHierarchyObject() and self.isGuideHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureGuideHierarchy:: is Object:: ", self.isGuideHierarchyObject(), " is in ViewPort:: ", self.isGuideHierarchyInViewport())
            return True
        if self.isGuideHierarchyObject() and not self.isGuideHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureGuideHierarchy:: is Object:: ", self.isGuideHierarchyObject(), " is in ViewPort:: ", self.isGuideHierarchyInViewport())
            self.guide_hierarchy_object.create()
            return True
        if not self.isGuideHierarchyObject() and self.isGuideHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureGuideHierarchy:: is Object:: ", self.isGuideHierarchyObject(), " is in ViewPort:: ", self.isGuideHierarchyInViewport())
            self.createGuideHierarchy()
            return True
        if not self.isGuideHierarchyObject() and not self.isGuideHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureGuideHierarchy:: is Object:: ", self.isGuideHierarchyObject(), " is in ViewPort:: ", self.isGuideHierarchyInViewport())
            self.createGuideHierarchy()
            self.guide_hierarchy_object.create()
            return True
        return False

    def getGuideHierarchyName(self):
        return self.guide_hierarchy_object.name

    def createRigHierarchy(self):
        self.rig_hierarchy_object = HierarchyObject(self, name = self.hierarchy_name, suffix = self.rig_hierarchy_suffix)

    def isRigHierarchy(self) -> bool:
        if self.rig_hierarchy is None:
            return False
        if not MC.objectExists(self.rig_hierarchy):
            return False
        return True
    
    def ensureComponentHierarchy(self):
        if self.components_hiearchy is not None:
                if not MC.objectExists(self.components_hiearchy):
                    self.components_hiearchy = MC.createTransform(self.scene.getSceneRigName() + RIG_HIERARCHY_COMPONENT_SUFFIX)
                    return True
                return False
        return True

    def getRigHierarchyName(self):
        return self.rig_hierarchy.name
    
    def updateGuideHierarchyName(self):
        self.hierarchy_name = self.scene.getSceneRigName()