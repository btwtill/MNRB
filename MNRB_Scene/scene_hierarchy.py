from collections import OrderedDict
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.global_variables import GUIDE_HIERARCHY_SUFFIX, RIG_HIERARCHY_SUFFIX #type: ignore

CLASS_DEBUG = True

class MNRB_Scene_Hierarchy(Serializable):
    def __init__(self, scene, guide_suffix = GUIDE_HIERARCHY_SUFFIX, rig_suffix = RIG_HIERARCHY_SUFFIX) -> None:
        super().__init__()

        self.scene = scene

        self.guide_suffix = guide_suffix
        self.rig_suffix = rig_suffix

        self.guide_hierarchy = None
        self.rig_hierarchy = None

        self.scene.properties.connectHasBeenModifiedCallback(self.updateGuideHierarchyName)

    def createGuideHierarchy(self):
        self.guide_hierarchy = MC.createTransform(self.scene.getSceneRigName() + self.guide_suffix)

    def createRigHierarchy(self):
        self.rig_hierarchy = MC.createTransform(self.scene.getSceneRigName() + self.rig_suffix)

    def isGuideHierarchy(self) -> bool:
        if CLASS_DEBUG: print("SCENE_RIG_HIERARCHY:: --isGuideHierarchy:: self.guide_hierarchy:: ", self.guide_hierarchy)
        return False if self.guide_hierarchy is None else MC.objectExists(self.guide_hierarchy)
    
    def isRigHierarchy(self) -> bool:
        return False if self.rig_hierarchy is None else MC.objectExists(self.rig_hierarchy)
    
    def getGuideHierarchyName(self):
        return self.guide_hierarchy
    
    def getRigHierarchyName(self):
        return self.rig_hierarchy
    
    def updateGuideHierarchyName(self):
        if self.guide_hierarchy is not None:
            try:
                current_guide_hierarchy = self.guide_hierarchy
                new_name = MC.renameObject(current_guide_hierarchy, self.scene.getSceneRigName() + self.guide_suffix)
                if new_name != self.guide_hierarchy:
                    self.guide_hierarchy = new_name
            except Exception as e:
                if CLASS_DEBUG: print("SCENE_HIERARCHY:: --updateGuideHierarchyName:: ERROR:: ", e)

    def serialize(self):
        serialized_data = OrderedDict([
            ('id', self.id), 
            ('guide_hierarchy', self.guide_hierarchy),
            ('rig_hierarchy', self.rig_hierarchy)
            ])
        return serialized_data
    
    def deserialize(self, data, hashmap = {}, restore_id = True):
        if restore_id: self.id = data['id']

        self.guide_hierarchy = data['guide_hierarchy']
        self.rig_hierarchy = ['rig_hierarchy']

        return True