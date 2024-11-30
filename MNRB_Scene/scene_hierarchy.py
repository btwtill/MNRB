from collections import OrderedDict
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Scene.scene_object import HierarchyObject #type: ignore
from MNRB.global_variables import GUIDE_HIERARCHY_SUFFIX, RIG_HIERARCHY_SUFFIX, RIG_HIERARCHY_COMPONENT_SUFFIX, RIG_HIERARCHY_SKELETON_SUFFIX, RIG_HIERARCHY_GEOMETRY_SUFFIX, RIG_HIERARCHY_SHAPES_SUFFIX #type: ignore

CLASS_DEBUG = True

class MNRB_Scene_Hierarchy(Serializable):
    def __init__(self, scene) -> None:
        super().__init__()

        self.scene = scene

        self.guide_hierarchy = None
        self.rig_hierarchy_top_node = None
        self.rig_hierarchy = []

        self.scene.properties.connectHasBeenModifiedCallback(self.updateGuideHierarchyName)

    def createGuideHierarchy(self):
        self.guide_hierarchy = HierarchyObject(self, name = self.scene.getSceneRigName(), suffix = GUIDE_HIERARCHY_SUFFIX)

    def createRigHierarchy(self):
        scene_rig_name = self.scene.getSceneRigName()
        self.rig_hierarchy_top_node = HierarchyObject(self, scene_rig_name + RIG_HIERARCHY_SUFFIX)
        self.rig_hierarchy.append(HierarchyObject(self.rig_hierarchy_top_node, scene_rig_name, suffix = RIG_HIERARCHY_COMPONENT_SUFFIX))
        self.rig_hierarchy.append(HierarchyObject(self.rig_hierarchy_top_node, scene_rig_name, suffix = RIG_HIERARCHY_SKELETON_SUFFIX))
        self.rig_hierarchy.append(HierarchyObject(self.rig_hierarchy_top_node, scene_rig_name, suffix = RIG_HIERARCHY_GEOMETRY_SUFFIX))
        self.rig_hierarchy.append(HierarchyObject(self.rig_hierarchy_top_node, scene_rig_name, suffix = RIG_HIERARCHY_SHAPES_SUFFIX))

    def isGuideHierarchy(self) -> bool:
        if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --isGuideHierarchy:: self.guide_hierarchy:: ", self.guide_hierarchy)
        return False if self.guide_hierarchy is None else MC.objectExists(self.guide_hierarchy.name)
    
    def isRigHierarchy(self) -> bool:
        if self.rig_hierarchy_top_node.name is None:
            return False
        if not MC.objectExists(self.rig_hierarchy_top_node.name):
            return False
        else:
            for hierarchy_object in self.rig_hierarchy:
                hierarchy_object.is_HierarchyObject()
            return True
    
    def getGuideHierarchyName(self):
        return self.guide_hierarchy.name
    
    def getRigHierarchyName(self):
        return self.rig_hierarchy_top_node.name
    
    def updateGuideHierarchyName(self):
        if self.guide_hierarchy is not None:
            try:
                current_guide_hierarchy = self.guide_hierarchy
                new_name = MC.renameObject(current_guide_hierarchy, self.scene.getSceneRigName() + GUIDE_HIERARCHY_SUFFIX)
                if new_name != self.guide_hierarchy:
                    self.guide_hierarchy = new_name
            except Exception as e:
                if CLASS_DEBUG: print("SCENE_HIERARCHY:: --updateGuideHierarchyName:: ERROR:: ", e)

    def serialize(self):
        rig_hierarchy = []
        for hierarchy_object in self.rig_hierarchy: rig_hierarchy.append(hierarchy_object.serialize())
        serialized_data = OrderedDict([
            ('id', self.id), 
            ('guide_hierarchy', self.guide_hierarchy),
            ('rig_hierarchy_top_node', self.rig_hierarchy_top_node),
            ('rig_hierarchy', rig_hierarchy)
            ])
        return serialized_data
    
    def deserialize(self, data, hashmap = {}, restore_id = True):
        if restore_id: self.id = data['id']
        
        if data['guide_hierarchy'] is not None:
            self.guide_hierarchy = HierarchyObject(self)
            self.guide_hierarchy.deserialize(data['guide_hierarchy'], hashmap, restore_id)

        if data['rig_hierarchy_top_node']:
            self.rig_hierarchy_top_node = HierarchyObject(self)
            self.rig_hierarchy_top_node.deserialize(data['rig_hierarchy_top_node'], hashmap, restore_id)

        for hierarchy_data in data['rig_hierarchy']:
            new_hierarchy_object = HierarchyObject(self.rig_hierarchy_top_node)
            new_hierarchy_object.deserialize(hierarchy_data, hashmap, restore_id)

        return True