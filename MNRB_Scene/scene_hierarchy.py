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
        
        self._hierarchy_name_changed_listeners = []

        self.scene.properties.connectHasBeenModifiedCallback(self.updateVirtualHierarchyName)

        self.createGuideHierarchy()
        self.createRigHierarchy()
        self.createSkeletonHierachy()


    @property
    def hierarchy_name(self): return self._hierarchy_name
    @hierarchy_name.setter
    def hierarchy_name(self, value):
        self._hierarchy_name = value

        for callback in self._hierarchy_name_changed_listeners: callback()

    def connectCallbackToHierarchyHasChanged(self, callback):
        self._hierarchy_name_changed_listeners.append(callback)

    def updateVirtualHierarchyName(self):
        if CLASS_DEBUG: print("%s:: --updateVirtualHierarchyName:: Old Name:: " % self.__class__.__name__, self.hierarchy_name, " New Name:: ", self.scene.getSceneRigName())
        self.hierarchy_name = self.scene.getSceneRigName()

    #guide Hierarchy
    def createGuideHierarchy(self):        
        self.guide_hierarchy_object = HierarchyObject(self, suffix = self.guide_hierarchy_suffix)
        if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --createGuideHierarchy:: self.guide_hierarchy_object:: ", self.guide_hierarchy_object)

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
            self.guide_hierarchy_object.draw()
            return True
        if not self.isGuideHierarchyObject() and self.isGuideHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureGuideHierarchy:: is Object:: ", self.isGuideHierarchyObject(), " is in ViewPort:: ", self.isGuideHierarchyInViewport())
            self.createGuideHierarchy()
            return True
        if not self.isGuideHierarchyObject() and not self.isGuideHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureGuideHierarchy:: is Object:: ", self.isGuideHierarchyObject(), " is in ViewPort:: ", self.isGuideHierarchyInViewport())
            self.createGuideHierarchy()
            self.guide_hierarchy_object.draw()
            return True
        return False

    def getGuideHierarchyName(self):
        return self.guide_hierarchy_object.name

    #rig Hierarchy
    def createRigHierarchy(self):
        self.rig_hierarchy_object = HierarchyObject(self, suffix = self.rig_hierarchy_suffix)

    def isRigHierarchyObject(self) -> bool:
        if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --isRigHierarchyObject:: self.guide_hierarchy_object:: ", self.rig_hierarchy_object)
        return False if self.rig_hierarchy_object is None else True
    
    def isRigHierarchyInViewport(self) -> bool:
        if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --isGuideHierarchyInViewport:: Guide Hierarchy is in Maya viewport:: ", MC.objectExists(self.hierarchy_name + self.rig_hierarchy_suffix))
        return MC.objectExists(self.hierarchy_name + self.rig_hierarchy_suffix)

    def ensureRigHierarchy(self):
        if self.isRigHierarchyObject() and self.isRigHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureRigHierarchy:: is Object:: ", self.isRigHierarchyObject(), " is in ViewPort:: ", self.isRigHierarchyInViewport())
            return True
        if self.isRigHierarchyObject() and not self.isRigHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureRigHierarchy:: is Object:: ", self.isRigHierarchyObject(), " is in ViewPort:: ", self.isRigHierarchyInViewport())
            self.rig_hierarchy_object.draw()
            return True
        if not self.isRigHierarchyObject() and self.isRigHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureRigHierarchy:: is Object:: ", self.isRigHierarchyObject(), " is in ViewPort:: ", self.isRigHierarchyInViewport())
            self.createRigHierarchy()
            return True
        if not self.isRigHierarchyObject() and not self.isRigHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureRigHierarchy:: is Object:: ", self.isRigHierarchyObject(), " is in ViewPort:: ", self.isRigHierarchyInViewport())
            self.createRigHierarchy()
            self.rig_hierarchy_object.draw()
            return True
        return False

    def getRigHierarchyName(self):
        return self.rig_hierarchy_object.name
    
    #skeleton hierarchy
    def createSkeletonHierachy(self):
        self.skeleton_hierarchy_object = HierarchyObject(self, parent = self.rig_hierarchy_object, suffix = self.skeleton_hiearchy_suffix)

    def isSkeletonHierarchyObject(self) -> bool:
        if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --isSkeletonHierarchyObject:: self.skeleton_hierarchy_object:: ", self.skeleton_hierarchy_object)
        return False if self.skeleton_hierarchy_object is None else True
    
    def isSkeletonHierarchyInViewport(self) -> bool:
        if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --isSkeletonHierarchyInViewport:: Skeleton Hierarchy is in Maya viewport:: ", MC.objectExists(self.hierarchy_name + self.skeleton_hiearchy_suffix))
        return MC.objectExists(self.hierarchy_name + self.skeleton_hiearchy_suffix)
    
    def ensureSkeletonHierarchy(self):
        if self.isSkeletonHierarchyObject() and self.isSkeletonHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureSkeletonHierarchy:: is Object:: ", self.isSkeletonHierarchyObject(), " is in ViewPort:: ", self.isSkeletonHierarchyInViewport())
            return True
        if self.isSkeletonHierarchyObject() and not self.isSkeletonHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureSkeletonHierarchy:: is Object:: ", self.isSkeletonHierarchyObject(), " is in ViewPort:: ", self.isSkeletonHierarchyInViewport())
            self.skeleton_hierarchy_object.draw()
            return True
        if not self.isSkeletonHierarchyObject() and self.isSkeletonHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureSkeletonHierarchy:: is Object:: ", self.isSkeletonHierarchyObject(), " is in ViewPort:: ", self.isSkeletonHierarchyInViewport())
            self.createSkeletonHierachy()
            return True
        if not self.isSkeletonHierarchyObject() and not self.isSkeletonHierarchyInViewport():
            if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --ensureSkeletonHierarchy:: is Object:: ", self.isSkeletonHierarchyObject(), " is in ViewPort:: ", self.isSkeletonHierarchyInViewport())
            self.createSkeletonHierachy()
            self.skeleton_hierarchy_object.draw()
            return True
        return False

    def getSkeletonHierarchyName(self):
        return self.skeleton_hierarchy_object.name