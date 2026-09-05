import hashlib
from collections import OrderedDict
from MNRB.ROSE_Data.rose_Editor_Serializable import Serializable #type: ignore
from MNRB.ROSE_naming.ROSE_names import ROSE_Names #type: ignore
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore

class deform(Serializable):
    def __init__(self, node, name = "", deserialized = False):
        super().__init__()

        self.node = node
        self.deform_name = name
        self.id = self.assembleStableId()
        self.name = self.assembleFullName()

        self.node.deforms.append(self)

        if not deserialized:
            self.draw()

    def draw(self, segment_scale_compensate = False):
        #take the name Maya actually gave the joint, not the one we asked for: if a
        #joint of that name is already in the scene (a previous build that wasn't
        #cleaned up) Maya uniquifies it, and keeping the requested name would leave
        #this object pointing at the *old* joint - which then gets bound, moved and
        #weighted instead of the one just created
        self.name = MC.createJoint(self.name)
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
        return self.node.getComponentPrefix() + self.node.getComponentName() + "_" + self.deform_name +  ROSE_Names.deform_suffix

    def assembleStableId(self):
        #derived, not generated: a deform object doesn't survive a rebuild
        #(staticBuild drops them all and the component recreates them), so a
        #generated id would change on every build and the skinning tab, which
        #stores deform references by id, would see the whole list as removed and
        #re-added. deform_name is the guide slot ("0", "pole", ...), unique within
        #a node and unaffected by renaming the component - unlike self.name, which
        #carries the component prefix and does change on a rename.
        key = "%s:%s" % (self.node.id, self.deform_name)
        return int.from_bytes(hashlib.sha1(key.encode()).digest()[:8], "big") >> 1
    
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
        self.deform_name = data['deform_name']

        #the stored id is ignored on purpose - this id is derived, so recomputing
        #it is what stops a project saved before that change from showing its
        #whole deform list as changed on first load. Cluster refs still holding an
        #old id resolve by name and self-heal in SkinningEditorCluster.resolveDeforms()
        self.id = self.assembleStableId()
        self.name = self.assembleFullName()

        return True
    