from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

CLASS_DEBUG = True

class VirtualHierarchyObject():
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
        self.name = MC.createTransform(self.hierarchy.hierarchy_name + self.suffix)
        if self.parent is not None:
            MC.parentObject(self.name, self.parent.name)

    def remove(self):
        MC.deleteObjectWithHierarchy(self.name)

    def exists(self):
        return MC.objectExists(self.name)

    def validateViewport(self):
        return MC.objectExists(self.rig_name + self.suffix)

    def ensureExistence(self):
        if CLASS_DEBUG: print("%s:: --ensureExistence:: " % self.__class__.__name__, self.suffix, " Current Rig Name:: ", self.rig_name)
        if self.validateViewport():
            return True
        else:
            self.draw()
            return True

    def updateRigName(self):
        if CLASS_DEBUG: print("%s:: --updateRigName:: Setting Rig_name old:: " % self.__class__.__name__, self.rig_name, " To New:: ", self.hierarchy.hierarchy_name)
        self.rig_name = self.hierarchy.hierarchy_name

    def updateName(self):
        if CLASS_DEBUG: print("%s:: --updateName:: old Rig Name:: "% self.__class__.__name__, self.rig_name)
        if CLASS_DEBUG: print("%s:: --updateName:: old Name:: "% self.__class__.__name__, self.name)
        
        if not self.exists():
            if CLASS_DEBUG: print("SCENE_HIERARCHY:: --updateHierarchyObject:: ", self.name, " Object is Not in the Viewport!!")
            self.updateRigName()
            self.name = self.rig_name + self.suffix
            return

        new_object_name = self.hierarchy.hierarchy_name + self.suffix
        if CLASS_DEBUG: print("%s:: --updateName:: new Name:: "% self.__class__.__name__, new_object_name)

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
        self.updateRigName()
    