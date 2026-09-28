from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_StepNode import PipelineStepNode #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_conf import registerPipelineStep #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.control_shape_switch import OPERATIONCODE_CONTROLSHAPESTEP #type: ignore

@registerPipelineStep(OPERATIONCODE_CONTROLSHAPESTEP)
class ControlShapeStep(PipelineStepNode):
    """Library control shapes from the Control Shapes tab.

    Unlike the other steps this is also a switch. Shapes are applied whenever a
    control is drawn - including builds started from the ROSE editor, which never
    pass through the pipeline - and disabling this step turns them off for all of
    those, not just for pipeline runs. See control_shape_switch.

    Running it redraws the controls that are already built, so it belongs after
    the Control Rig step; it is harmless anywhere, since a fresh build already
    drew them with their shapes.
    """

    operation_code = OPERATIONCODE_CONTROLSHAPESTEP
    operation_title = "Control Shapes"
    icon = ""

    def runStep(self):
        control_shape_tab = getattr(self.scene, "control_shape_tab", None)
        if control_shape_tab is None:
            return False, "No control shape tab available"

        return control_shape_tab.onApplyToRig()
