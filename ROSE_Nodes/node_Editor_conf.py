from MNRB.ROSE_UI.node_Editor_Exceptions.node_Editor_RegistrationException import InvalidNodeRegistration, OperationCodeNotRegistered #type: ignore

NODELIST_MIMETYPE = "application/x-item"

OPERATIONCODE_BASECOMPONENT = 0
OPERATIONCODE_SINGLEDEFORMCOMPONENT = 1
OPERATIONCODE_MULTIDEFORMCOMPONENT = 2

OPERATIONCODE_SIMPLEIKCOMPONENT = 3

ROSE_NODE_GROUPS = {
    '0' : ('Base_Components', [0, 1, 2]),
    '1' : ('Simple_Components', [3]),
}

ROSE_NODES = {

}

def registerNodesInROSENodes(operation_code, class_reference):
    if operation_code in ROSE_NODES:
        raise InvalidNodeRegistration("Duplicate Node Registration of '%s'. There is already %s" % (operation_code, ROSE_NODES[operation_code]))
    ROSE_NODES[operation_code] = class_reference

def registerNode(operation_code):
    def decorator(original_class):
        registerNodesInROSENodes(operation_code, original_class)
        return original_class
    return decorator

def getClassFromOperationCode(operation_code):
    if operation_code not in ROSE_NODES: raise OperationCodeNotRegistered("Operation Code '%s' is not registered" % operation_code)
    return ROSE_NODES[operation_code]

from MNRB.ROSE_Nodes.Nodes import * #type: ignore