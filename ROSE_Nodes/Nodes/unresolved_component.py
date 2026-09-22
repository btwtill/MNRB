import copy

from MNRB.ROSE_Nodes.node_Editor_conf import resolveTypeId #type: ignore
from MNRB.ROSE_Nodes.rose_node_base import ROSE_Node #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")

class UnresolvedComponentNode(ROSE_Node):
    """Stands in for a component whose type is not registered in this session.

    Deliberately NOT decorated with @registerNode: it is never something the user
    picks from the palette, only something a load falls back to when a graph
    references a node type that this install does not have - typically a rig-
    specific pack that has not been added.

    The contract is narrow and the whole point of the class: **serialize() gives
    back exactly what was loaded.** Opening a shared rig without its pack and
    saving must not quietly drop those components, which is what raising
    OperationCodeNotRegistered and losing the node would eventually amount to.
    It is the same failure the skinning loader had - a load that cannot resolve
    something, followed by a save that writes the gap out as permanent.
    """

    type_id = "rose.unresolved"
    operation_title = "Unresolved Component"
    icon = ""
    #no category, so it never appears in the drag list
    category = None

    def __init__(self, scene, inputs = [], outputs = [], color = None):
        super().__init__(scene, inputs, outputs)

        self.raw_data = None
        self.missing_type_id = None

    def getMissingTypeId(self):
        return self.missing_type_id

    def getMissingPackId(self):
        """The pack prefix of the missing type, for a "this rig requires …" summary."""
        if not self.missing_type_id or "." not in str(self.missing_type_id):
            return None
        return str(self.missing_type_id).split(".")[0]

    def socketDefinitionsFrom(self, socket_data_list):
        return [(socket_data["socket_value"], socket_data["socket_type"],
                 socket_data.get("accept_multi_edges", True))
                for socket_data in socket_data_list]

    def deserialize(self, data, hashmap = {}, restore_id = True, exists = False):
        #kept before anything else can fail, so serialize() can always give it back
        self.raw_data = copy.deepcopy(data)
        self.missing_type_id = resolveTypeId(data.get("type_id", data.get("operation_code")))

        #sockets are rebuilt to match the file rather than the class, because the
        #base deserialize indexes self.inputs[index] and because the edges in the
        #graph reference these sockets by id - without them the node would survive
        #but every connection to it would be dropped
        self.initSockets(self.socketDefinitionsFrom(data.get("inputs", [])),
                         self.socketDefinitionsFrom(data.get("outputs", [])))

        try:
            super().deserialize(data, hashmap, restore_id, exists)
        except Exception as error:
            #best effort: the visual restore may fail on component-specific data
            #this class knows nothing about, which does not matter because the
            #file content is already safe in raw_data
            log.warning("UNRESOLVED:: --deserialize:: partial restore of '%s': %s"
                        % (self.missing_type_id, error))

        self.title = "%s  (type not registered)" % self.missing_type_id
        self.properties.setInvalid()
        self.properties.updateActionButtons()

        return True

    def serialize(self):
        if self.raw_data is None:
            return super().serialize()

        data = copy.deepcopy(self.raw_data)

        #position is the one thing the user can legitimately change on a node they
        #cannot otherwise edit, so it is the only field allowed to differ
        try:
            data["position_x"] = self.grNode.scenePos().x()
            data["position_y"] = self.grNode.scenePos().y()
        except Exception:
            pass

        return data

# Builds are refused rather than attempted

    def guideBuild(self):
        log.warning("UNRESOLVED:: cannot build '%s' - its node type is not registered" % self.missing_type_id)
        return False

    def staticBuild(self):
        return False

    def componentBuild(self):
        return False

    def connectComponent(self):
        return False
