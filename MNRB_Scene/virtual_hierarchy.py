from MNRB.MNRB_Scene.virtual_hierarchy_object import VirtualHierarchyObject #type: ignore
from MNRB.global_variables import GUIDE_HIERARCHY_SUFFIX, RIG_HIERARCHY_SUFFIX, RIG_HIERARCHY_COMPONENT_SUFFIX, RIG_HIERARCHY_SKELETON_SUFFIX, RIG_HIERARCHY_GEOMETRY_SUFFIX, RIG_HIERARCHY_SHAPES_SUFFIX #type: ignore

CLASS_DEBUG = True

class MNRB_Virtual_Hierarchy():
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

        self.initHierarchy()
        
    @property
    def hierarchy_name(self): return self._hierarchy_name
    @hierarchy_name.setter
    def hierarchy_name(self, value):
        self._hierarchy_name = value

        for callback in self._hierarchy_name_changed_listeners: callback()

    def initHierarchy(self):
        self.guide_hierarchy_object = VirtualHierarchyObject(self, suffix = GUIDE_HIERARCHY_SUFFIX)
        self.rig_hierarchy_object = VirtualHierarchyObject(self, suffix = self.rig_hierarchy_suffix)
        self.skeleton_hierarchy_object = VirtualHierarchyObject(self, parent = self.rig_hierarchy_object, suffix = self.skeleton_hiearchy_suffix)

    def connectCallbackToHierarchyHasChanged(self, callback):
        self._hierarchy_name_changed_listeners.append(callback)

    def updateVirtualHierarchyName(self):
        if CLASS_DEBUG: print("%s:: --updateVirtualHierarchyName:: Old Name:: " % self.__class__.__name__, self.hierarchy_name, " New Name:: ", self.scene.getSceneRigName())
        self.hierarchy_name = self.scene.getSceneRigName()