import hashlib
from collections import OrderedDict
from MNRB.ROSE_Data.rose_Editor_Serializable import Serializable #type: ignore
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.ROSE_Attributes.attribute_types import AttributeType, mapNameToAttributeType #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")

class attribute(Serializable):
    """One attribute a component deliberately exposes.

    Exposed is the whole point: a component creates plenty of attributes for its
    own internal wiring, and those should never show up in the Attribute Editor.
    Only what a component registers through ROSE_Node.exposeAttribute() - i.e.
    what ends up in this list - is offered for proxying onto a control.

    Declared at node construction (ROSE_Node.initAttributes) rather than at build
    time, so the Attribute Editor can list a component's attributes before the rig
    has ever been built.
    """

    def __init__(self, node, name = "", attribute_type = AttributeType.FLOAT,
                 default_value = 0, minimum = None, maximum = None,
                 options = None, keyable = True):
        super().__init__()

        self.node = node
        self.attribute_name = name
        self.attribute_type = attribute_type

        self.default_value = default_value
        self.minimum = minimum
        self.maximum = maximum
        #enum only - the ordered option names
        self.options = options if options is not None else []
        self.keyable = keyable

        self.id = self.assembleStableId()

        self.node.attributes.append(self)

    def assembleStableId(self):
        #derived, same reasoning as deform/control: this object is rebuilt every
        #time initAttributes() runs, and the Attribute Editor stores which
        #attributes it assigned to which control by id
        key = "%s:%s" % (self.node.id, self.attribute_name)
        return int.from_bytes(hashlib.sha1(key.encode()).digest()[:8], "big") >> 1

    def getHostNode(self):
        """The Maya node this attribute lives on.

        A component's attributes sit on its component hierarchy transform. An
        attribute that belongs to no component lives on the rig root instead -
        that variant overrides this.
        """
        return self.node.component_hierarchy

    def getDisplayName(self):
        return "%s%s" % (self.node.getComponentFullPrefix(), self.attribute_name)

    def exists(self):
        host_node = self.getHostNode()
        if host_node is None or not MC.objectExists(host_node):
            return False
        return MC.attributeExists(host_node, self.attribute_name)

    def create(self):
        """Add this attribute to its host in the Maya scene."""
        host_node = self.getHostNode()

        if host_node is None or not MC.objectExists(host_node):
            log.debug("ATTRIBUTE:: --create:: no host node for", self.attribute_name)
            return False

        #componentBuild recreates the hierarchy each time, so this normally starts
        #from a clean node - the guard is for a partial/repeated build
        if MC.attributeExists(host_node, self.attribute_name):
            return True

        if self.attribute_type == AttributeType.BOOL:
            MC.addBoolAttribute(host_node, self.attribute_name, self.default_value, self.keyable)
        elif self.attribute_type == AttributeType.INT:
            MC.addIntAttribute(host_node, self.attribute_name, self.default_value,
                               self.minimum, self.maximum, self.keyable)
        elif self.attribute_type == AttributeType.ENUM:
            MC.addEnumAttribute(host_node, self.attribute_name, self.options,
                                self.default_value, self.keyable)
        else:
            MC.addFloatAttribute(host_node, self.attribute_name, self.default_value,
                                 self.minimum, self.maximum, self.keyable)

        return True

    def remove(self):
        if self.exists():
            MC.deleteAttribute(self.getHostNode(), self.attribute_name)

    def proxyOnto(self, target_node, proxy_name = None):
        """Put this attribute onto another node as a proxy - the Attribute
        Editor's build step uses this to place it on a control."""
        if not self.exists():
            log.debug("ATTRIBUTE:: --proxyOnto:: source does not exist:", self.attribute_name)
            return False

        proxy_name = proxy_name if proxy_name is not None else self.attribute_name

        if MC.attributeExists(target_node, proxy_name):
            return True

        MC.addProxyAttribute(target_node, proxy_name, self.getHostNode(), self.attribute_name)
        return True

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('attribute_name', self.attribute_name),
            ('attribute_type', self.attribute_type.value),
            ('default_value', self.default_value),
            ('minimum', self.minimum),
            ('maximum', self.maximum),
            ('options', self.options),
            ('keyable', self.keyable),
        ])

    def deserialize(self, data, hashmap = {}, restore_id = True):
        self.attribute_name = data['attribute_name']
        self.attribute_type = mapNameToAttributeType(data['attribute_type'])
        self.default_value = data.get('default_value', 0)
        self.minimum = data.get('minimum', None)
        self.maximum = data.get('maximum', None)
        self.options = data.get('options', [])
        self.keyable = data.get('keyable', True)

        #derived, so recomputed rather than restored
        self.id = self.assembleStableId()

        return True

    def __str__(self):
        return "attribute(%s, %s)" % (self.attribute_name, self.attribute_type.value)
