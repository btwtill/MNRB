from collections import OrderedDict
from MNRB.ROSE_Attributes.attribute import attribute #type: ignore
from MNRB.ROSE_Attributes.attribute_types import AttributeType, mapNameToAttributeType #type: ignore
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore

#a fixed id rather than a generated one: attribute ids derive from their host's
#id, and these have to stay stable across sessions the same way a component
#node's restored id does. There is only ever one of these.
RIG_ROOT_HOST_ID = 1

class RigRootAttributeHost:
    """Owner for attributes that belong to the rig rather than to any component.

    Deliberately duck-types the small part of ROSE_Node that `attribute` actually
    touches - `id`, `attributes`, `component_hierarchy` and
    `getComponentFullPrefix()` - so those attributes need no special casing:
    they create, proxy and resolve through exactly the same code paths, just
    hosted on the rig root, which exists whether or not any component does.
    """

    def __init__(self, scene):
        self.id = RIG_ROOT_HOST_ID
        self.scene = scene
        self.attributes = []

    @property
    def component_hierarchy(self):
        #what attribute.getHostNode() reads. Resolved live rather than cached,
        #since the rig root is named after the scene's rig name and can change.
        rig_hierarchy_object = self.scene.virtual_rig_hierarchy.rig_hierarchy_object
        return rig_hierarchy_object.name

    def getComponentFullPrefix(self):
        #custom attributes carry no component prefix - the name the user typed is
        #the whole name
        return ""

    def ensureHostExists(self):
        return self.scene.virtual_rig_hierarchy.rig_hierarchy_object.ensureExistence()

    def addAttribute(self, name, attribute_type = AttributeType.FLOAT, default_value = 0,
                     minimum = None, maximum = None, options = None, keyable = True):
        if self.getAttributeByName(name) is not None:
            return None
        return attribute(self, name, attribute_type, default_value, minimum, maximum, options, keyable)

    def removeAttribute(self, attribute_id):
        for custom_attribute in list(self.attributes):
            if custom_attribute.id == attribute_id:
                custom_attribute.remove()
                self.attributes.remove(custom_attribute)
                return True
        return False

    def getAttributeByName(self, name):
        for custom_attribute in self.attributes:
            if custom_attribute.attribute_name == name:
                return custom_attribute
        return None

    def buildAttributes(self):
        if not self.ensureHostExists():
            return False
        for custom_attribute in self.attributes:
            self.rebuildIfDefinitionChanged(custom_attribute)
            custom_attribute.create()
        return True

    def rebuildIfDefinitionChanged(self, custom_attribute):
        """Recreate an attribute whose scene copy no longer matches its definition.

        create() deliberately leaves an existing attribute alone, so editing an
        enum's options here would otherwise never reach Maya. Recreating is safe
        for these specifically: they are ROSE-owned, and the graph build remakes
        every connection and proxy immediately afterwards.
        """
        if not custom_attribute.exists():
            return

        host_node = custom_attribute.getHostNode()
        if not self.definitionHasChanged(custom_attribute, host_node):
            return

        #hold the current value across the recreate where it is still meaningful
        previous_value = MC.getAttribute(host_node, custom_attribute.attribute_name)

        custom_attribute.remove()
        custom_attribute.create()

        self.restoreValue(custom_attribute, host_node, previous_value)

    def restoreValue(self, custom_attribute, host_node, previous_value):
        if previous_value is None:
            return

        if custom_attribute.attribute_type == AttributeType.ENUM:
            #an option that no longer exists would be out of range
            if isinstance(previous_value, int) and 0 <= previous_value < len(custom_attribute.options):
                MC.setAttribute(host_node, custom_attribute.attribute_name, previous_value)
            return

        if custom_attribute.minimum is not None and previous_value < custom_attribute.minimum:
            return
        if custom_attribute.maximum is not None and previous_value > custom_attribute.maximum:
            return

        MC.setAttribute(host_node, custom_attribute.attribute_name, previous_value)

    def definitionHasChanged(self, custom_attribute, host_node):
        attribute_name = custom_attribute.attribute_name

        if MC.getAttributeDefault(host_node, attribute_name) != custom_attribute.default_value:
            return True

        if custom_attribute.attribute_type == AttributeType.ENUM:
            return MC.getAttributeEnumOptions(host_node, attribute_name) != custom_attribute.options

        if custom_attribute.attribute_type in (AttributeType.INT, AttributeType.FLOAT):
            #limits live on the source attribute - a proxy inherits them, and Maya
            #refuses a setAttr past the maximum through the proxy too
            return (MC.getAttributeMinimum(host_node, attribute_name) != custom_attribute.minimum
                    or MC.getAttributeMaximum(host_node, attribute_name) != custom_attribute.maximum)

        return False

    def serialize(self):
        return OrderedDict([
            ('attributes', [custom_attribute.serialize() for custom_attribute in self.attributes]),
        ])

    def deserialize(self, data, hashmap = {}, restore_id = True):
        self.attributes = []
        for attribute_data in data.get('attributes', []):
            restored = attribute(self, attribute_data['attribute_name'],
                                 mapNameToAttributeType(attribute_data['attribute_type']))
            restored.deserialize(attribute_data, hashmap, restore_id)
        return True
