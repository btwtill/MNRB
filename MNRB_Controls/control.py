from collections import OrderedDict
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.MNRB_Controls.control_types import control_types #type: ignore
from MNRB.MNRB_Controls.control_shape_circle import control_shape_circle #type: ignore

class control(Serializable):
    def __init__(self, node, name = "", parent = None, control_type = control_types.circle, deserialized = False):
        super().__init__()

        self.node = node
        self.node.controls.append(self)
         
        self.control_name  = name
        self.name = self.assembleFullName()

        self.parent = parent

        self._control_type = control_type
        self.control_shape = self.determinControlShape()(self)

        if not deserialized:
            self.draw()

    @property
    def control_type(self): return self._control_type
    @control_type.setter
    def control_type(self, value):
        self._control_type = value

        self.control_shape = self.determinControlShape()(self)

    def assembleFullName(self):
        return self.node.getComponentPrefix() + self.node.getComponentName() + self.control_name + MNRB_Names.control_suffix

    def draw(self):
        self.control_shape.draw()
        if self.parent is not None:
            MC.parentObject(self.name, self.parent.name)

    def resize(self):
        self.control_shape.resize()

    def determinControlShape(self):
        return control_shape_circle

    def serialize(self):
        serialized_data = OrderedDict([
            ('id', self.id),
            ('control_name', self.control_name),
            ('parent', self.parent.id if self.parent is not None else None),
            ('control_type', self.control_type)
        ])
        return serialized_data
    
    def deserialize(self, data, hashmap = {}, restore_id = True):
        if restore_id: self.id = data['id']

        self.control_name = data['control_name']
        self.control_type = data['control_type']

        return True
