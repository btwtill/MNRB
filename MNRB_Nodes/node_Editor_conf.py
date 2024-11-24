from MNRB.MNRB_UI.node_Editor_Exceptions.node_Editor_RegistrationException import InvalidNodeRegistration, OperationCodeNotRegistered #type: ignore

NODELIST_MIMETYPE = "application/x-item"

OPERATIONCODE_BASECOMPONENT = 0
OPERATIONCODE_TESTCOMPONENT = 1


MNRB_NODES = {

}

def registerNodesInMNRBNodes(operation_code, class_reference):
    if operation_code in MNRB_NODES:
        raise InvalidNodeRegistration("Duplicate Node Registration of '%s'. There is already %s" % (operation_code, MNRB_NODES[operation_code]))
    MNRB_NODES[operation_code] = class_reference

def registerNode(operation_code):
    def decorator(original_class):
        registerNodesInMNRBNodes(operation_code, original_class)
        return original_class
    return decorator

def getClassFromOperationCode(operation_code):
    if operation_code not in MNRB_NODES: raise OperationCodeNotRegistered("Operation Code '%s' is not registered" % operation_code)
    return MNRB_NODES[operation_code]

from MNRB.MNRB_Nodes.Nodes import * #type: ignore