from collections import OrderedDict
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_naming.MNRB_names import MNRB_Names #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

class deform(Serializable):
    def __init__(self, node, name = "", parent = None, deserialized = False):
        super().__init__()

        self.node = node
        self.deform_name = name
        self.name = self.node.getComponentPrefix() + self.node.getComponentName() + "_" + self.deform_name +  MNRB_Names.deform_suffix

        self.parent = parent

        self.node.deforms.append(self)

        if not deserialized:
            self.draw()

    def draw(self):
        MC.createJoint(self.name)
        if self.parent is not None:
            MC.parentObject(self.name, self.parent.name)
    
    def exists(self):
        return MC.objectExists(self.name)

    def remove(self):
        if self.exists():
            MC.deleteNode(self.name)
    
    def updateName(self, has_duplicate_names):
        pass

    def serialize(self):
        serialized_data = OrderedDict([
            ('id', self.id),
            ('deform_name', self.deform_name),
            ('parent', self.parent.id if self.parent is not None else None)
        ])

        return serialized_data
    
    def deserialize(self, data, hashmap = {}, restore_id = True):

        if restore_id: self.id = data['id']
        self.deform_name = data['deform_name']

        self.name = self.node.getComponentPrefix() + self.node.getComponentName() + "_" + self.deform_name + MNRB_Names.deform_suffix

        if data['parent'] is not None:
            hashmap[self.id] = data['parent']

        return True
    