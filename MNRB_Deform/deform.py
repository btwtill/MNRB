from collections import OrderedDict
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_Naming.MNRB_names import MNRB_Names #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

class deform(Serializable):
    def __init__(self, node, name = "", deserialized = False):
        super().__init__()

        self.node = node
        self.deform_name = name
        self.name = self.assembleFullName()

        self.node.deforms.append(self)

        if not deserialized:
            self.draw()

    def draw(self, segment_scale_compensate = False):
        MC.createJoint(self.name)
        MC.setAttribute(self.name, "segmentScaleCompensate", segment_scale_compensate)
        self.resize(self.node.properties.deform_size)
    
    def exists(self):
        return MC.objectExists(self.name)

    def remove(self):
        if self.exists():
            MC.deleteNode(self.name)
    
    def resize(self, size):
        if self.exists():
            MC.setJointRadius(self.name, size)

    def assembleFullName(self):
        return self.node.getComponentPrefix() + self.node.getComponentName() + "_" + self.deform_name +  MNRB_Names.deform_suffix
    
    def updateName(self, has_duplicate_names):
        if self.exists():
            new_name = self.assembleFullName()

            if self.name == new_name:
                return

            if has_duplicate_names:
                duplicates = MC.findDuplicatesInNodeHiearchyByName(self.node.scene.virtual_rig_hierarchy.skeleton_hierarchy_object.name, new_name)
                if duplicates != []:
                    new_name = new_name + str(duplicates[1])
            self.name = MC.renameObject(self.name, new_name)

    def select(self):
        if self.exists():
            MC.selectObject(self.name)

    def setPosition(self, matrix, clear_Orient=True):
        MC.setObjectWorldPositionMatrix(self.name, matrix)
        if clear_Orient:
            MC.applyTransformRotate(self.name)
            MC.applyTransformScale(self.name)

    def setSegmentScaleCompensate(self, value):
        if self.exists():
            MC.setAttribute(self.name, "segmentScaleCompensate", value)

    def serialize(self):
        serialized_data = OrderedDict([
            ('id', self.id),
            ('deform_name', self.deform_name)
        ])

        return serialized_data
    
    def deserialize(self, data, hashmap = {}, restore_id = True):

        if restore_id: self.id = data['id']
        self.deform_name = data['deform_name']

        self.name = self.assembleFullName()


        return True
    