from MNRB.MNRB_UI.node_Editor_Exceptions.node_Editor_RegistrationException import InvalidNodeRegistration, OperationCodeNotRegistered #type: ignore

#separate registry from MNRB_Nodes/node_Editor_conf.py's MNRB_NODES/operation codes -
#pipeline steps and rig components are two different canvases with two different
#node vocabularies, and keeping the registries apart means the two operation-code
#spaces can never collide

PIPELINE_STEP_GROUPS = {
    '0': ('Build Steps', []),
}

PIPELINE_STEPS = {

}

def registerStepInPipelineSteps(operation_code, class_reference):
    if operation_code in PIPELINE_STEPS:
        raise InvalidNodeRegistration("Duplicate Pipeline Step Registration of '%s'. There is already %s" % (operation_code, PIPELINE_STEPS[operation_code]))
    PIPELINE_STEPS[operation_code] = class_reference
    PIPELINE_STEP_GROUPS['0'][1].append(operation_code)

def registerPipelineStep(operation_code):
    def decorator(original_class):
        registerStepInPipelineSteps(operation_code, original_class)
        return original_class
    return decorator

def getClassFromOperationCode(operation_code):
    if operation_code not in PIPELINE_STEPS: raise OperationCodeNotRegistered("Operation Code '%s' is not registered" % operation_code)
    return PIPELINE_STEPS[operation_code]

from MNRB.MNRB_UI.pipeline_Editor_UI.steps import * #type: ignore
