from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

class HierarchyObject():
    def __init__(self, hierarchy, parent = None, suffix = ""):
        self.hierarchy = hierarchy

        self.parent = parent
        self.rig_name = self.hierarchy.hierarchy_name
        self.suffix = suffix
        self._name = self.rig_name + self.suffix

        self.hierarchy.connectCallbackToHierarchyHasChanged(self.updateName)
            
    @property
    def name(self): return self._name
    @name.setter
    def name(self, value):
        self._name = value

    def draw(self):
        self.name = MC.createTransform(self.name)
        if self.parent is not None:
            MC.parentObject(self.name, self.parent.name)

    def remove(self):
        MC.deleteObjectWithHierarchy(self.name)

    def exists(self):
        return MC.objectExists(self.name)

    def updateName(self):
        try:
            new_object_name = self.hierarchy.hierarchy_name + self.suffix

            if self.name == new_object_name:
                return
            
            if self.parent is None:
                duplicates = []
            else:
                duplicates = MC.findDuplicatesInNodeHiearchyByName(self.parent.name, new_object_name)
            if duplicates != []:
                new_object_name = new_object_name + str(duplicates[1])
            
            new_name = MC.renameObject(self.name, new_object_name)
            self.name = new_name
        except Exception as e:
            print("SCENE_HIERARCHY:: --updateGuideHierarchyName:: ERROR:: ", e)