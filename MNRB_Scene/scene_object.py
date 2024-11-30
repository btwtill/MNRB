from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

class HierarchyObject(Serializable):
    def __init__(self, parent, name = "Undefined"):
        self.parent = parent
        
        self.name = name

    def create(self):
        self.name = MC.createTransform(self.name)

    def remove(self):
        MC.deleteObjectWithHierarchy(self.name)

    def updateName(self):
        pass