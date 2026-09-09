from MNRB.ROSE_UI.node_Editor_Exceptions.node_Editor_RegistrationException import InvalidNodeRegistration, OperationCodeNotRegistered #type: ignore

#a third registry alongside ROSE_NODES (rig components) and PIPELINE_STEPS (build
#steps). Three canvases, three node vocabularies, three operation-code spaces that
#can never collide with each other.

OPERATIONCODE_ATTRIBUTE_NODE = 0
OPERATIONCODE_CONTROL_NODE = 1
OPERATIONCODE_REVERSE_NODE = 2
OPERATIONCODE_MULTIPLY_NODE = 3
OPERATIONCODE_CONDITION_NODE = 4
OPERATIONCODE_CLAMP_NODE = 5
OPERATIONCODE_SCENE_TARGET_NODE = 6

#re-exported from the leaf module so callers can keep importing them from here.
#They cannot be *defined* here: conf imports every node module at the bottom, so
#anything conf reaches must not import conf back.
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_categories import (CATEGORY_SOURCE, #type: ignore
                                                                          CATEGORY_TARGET,
                                                                          CATEGORY_OPERATOR)

#what the canvas's right-click menu offers. Attribute and Control nodes are
#absent on purpose - they come from the palettes, so they can never be created
#without something real behind them.
ATTRIBUTE_NODE_GROUPS = {
    '0': ('Operators', [OPERATIONCODE_REVERSE_NODE, OPERATIONCODE_MULTIPLY_NODE,
                        OPERATIONCODE_CONDITION_NODE, OPERATIONCODE_CLAMP_NODE]),
    '1': ('Targets', [OPERATIONCODE_SCENE_TARGET_NODE]),
}

ATTRIBUTE_NODES = {}

def registerNodeInAttributeNodes(operation_code, class_reference):
    if operation_code in ATTRIBUTE_NODES:
        raise InvalidNodeRegistration("Duplicate Attribute Node Registration of '%s'. There is already %s"
                                      % (operation_code, ATTRIBUTE_NODES[operation_code]))
    ATTRIBUTE_NODES[operation_code] = class_reference

def registerAttributeNode(operation_code):
    def decorator(original_class):
        registerNodeInAttributeNodes(operation_code, original_class)
        return original_class
    return decorator

def getClassFromOperationCode(operation_code):
    if operation_code not in ATTRIBUTE_NODES:
        raise OperationCodeNotRegistered("Operation Code '%s' is not registered" % operation_code)
    return ATTRIBUTE_NODES[operation_code]

from MNRB.ROSE_UI.attribute_Editor_UI.graph_nodes import * #type: ignore
