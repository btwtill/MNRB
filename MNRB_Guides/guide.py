from collections import OrderedDict
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore

class guide(Serializable):
    def __init__(self, name, color = (1, 1, 0), position = (0, 0, 0), size = 1) -> None:
        super().__init__()

        self.name = name
        self.color = color

        self.position = position
        self.size = 1

    def draw(self):
        guide_shape = MC.createSpaceLocator(self.position, self.name, self.color)
        self.name = guide_shape

    def resize(self, size):
        MC.setLocatorLocalScale(self.name, size)

    def serialize(self):
        serialized_data = OrderedDict([
            ('id', self.id),
            ('name', self.name)
        ])
        return serialized_data

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.id = data['id']
        return True