from MNRB.ROSE_UI.node_Editor_Exceptions.node_Editor_RegistrationException import InvalidNodeRegistration, OperationCodeNotRegistered #type: ignore

NODELIST_MIMETYPE = "application/x-item"

#Node types are identified by a namespaced string, "<pack>.<name>". The prefix
#belongs to whoever ships the pack, so two people adding a node cannot collide
#without also picking the same pack name.
#
#This replaced integer operation codes, where two packs both choosing 4 produced
#files that deserialised into each OTHER's component type - a wrong rig rather
#than an error, which is the worst way for it to fail. Reserved integer ranges
#were the alternative and need exactly the central coordination that is missing
#when nodes get shared informally.
TYPEID_BASECOMPONENT = "rose.base"
TYPEID_SINGLEDEFORMCOMPONENT = "rose.single_deform"
TYPEID_MULTIDEFORMCOMPONENT = "rose.multi_deform"
TYPEID_SIMPLEIKCOMPONENT = "rose.simple_ik"

#graphs saved before type ids stored these integers. Permanent - old project
#files stay openable.
LEGACY_OPERATION_CODES = {
    0: TYPEID_BASECOMPONENT,
    1: TYPEID_SINGLEDEFORMCOMPONENT,
    2: TYPEID_MULTIDEFORMCOMPONENT,
    3: TYPEID_SIMPLEIKCOMPONENT,
}

#category id -> [label, sort order]. A node names its own category, so adding one
#touches only the node instead of a central membership list; packs contribute
#further categories through their manifest.
ROSE_NODE_CATEGORIES = {
    "rose.base_components": ["Base_Components", 0],
    "rose.simple_components": ["Simple_Components", 1],
}

ROSE_NODES = {}

def resolveTypeId(stored_value):
    """A node type id from either file format."""
    if isinstance(stored_value, bool):
        return stored_value
    if isinstance(stored_value, int):
        return LEGACY_OPERATION_CODES.get(stored_value, stored_value)
    if isinstance(stored_value, str) and stored_value.isdigit():
        return LEGACY_OPERATION_CODES.get(int(stored_value), stored_value)
    return stored_value

def registerNodeCategory(category_id, label, order = 100):
    ROSE_NODE_CATEGORIES[category_id] = [label, order]

def getNodeCategories():
    """(category_id, label) in display order."""
    return [(category_id, value[0]) for category_id, value
            in sorted(ROSE_NODE_CATEGORIES.items(), key = lambda item: (item[1][1], item[1][0]))]

def getNodeClassesInCategory(category_id):
    return [node_class for node_class in ROSE_NODES.values()
            if getattr(node_class, "category", None) == category_id]

def registerNodesInROSENodes(type_id, class_reference):
    if type_id in ROSE_NODES:
        raise InvalidNodeRegistration("Duplicate Node Registration of '%s'. There is already %s" % (type_id, ROSE_NODES[type_id]))
    ROSE_NODES[type_id] = class_reference

def registerNode(type_id):
    def decorator(original_class):
        registerNodesInROSENodes(type_id, original_class)
        return original_class
    return decorator

def getClassFromTypeId(type_id):
    type_id = resolveTypeId(type_id)
    if type_id not in ROSE_NODES:
        raise OperationCodeNotRegistered("Node type '%s' is not registered" % type_id)
    return ROSE_NODES[type_id]

from MNRB.ROSE_Nodes.Nodes import * #type: ignore
