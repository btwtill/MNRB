NODELIST_MIMETYPE = "application/x-item"

OPERATION_BASECOMPONENT = 0
OPERATION_TESTCOMPONENT = 1


MNRB_NODES = {

}


def registerNodesInMNRBNodes(operation_code, class_reference):
    if operation_code in MNRB_NODES:
        raise InvalidNodeRegistration("Duplicate Node Registration of '%s'. There is already %s" % (operation_code, MNRB_NODES[operation_code]))
    MNRB_NODES[operation_code] = class_reference