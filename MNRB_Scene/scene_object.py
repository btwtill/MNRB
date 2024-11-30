from collections import OrderedDict
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

class HierarchyObject(Serializable):
    def __init__(self, parent = None, name = "Undefined", suffix = ""):
        self.parent = parent
        self.suffix = suffix
        self.scene_name = name
        self._name = self.scene_name + self.suffix

        if self.parent is not None and self.scene_name != "Undefined":
            self.create()
            
    @property
    def name(self): return self._name
    @name.setter
    def name(self, value):
        self._name = value

    def create(self):
        self.name = MC.createTransform(self.name)
        MC.parentObject(self.name, self.parent.name)

    def remove(self):
        MC.deleteObjectWithHierarchy(self.name)

    def is_HierarchyObject(self):
        if self.name != "Undefined":
            if not MC.objectExists(self.name):
                self.create()
                return True
            return True
        return False
    
    def updateName(self):
        pass

    def serialize(self):
        serialized_data = OrderedDict([
            ('id', self.id),
            ('scene_name', self.scene_name),
            ('suffix', self.suffix)
        ])
        return serialized_data
    
    def deserialize(self, data, hashmap = {}, restore_id=True):
        if restore_id: self.id = id

        self.scene_name = data['scene_name']
        self.suffix = data['suffix']
        self.name = self.scene_name + self.suffix

        return True