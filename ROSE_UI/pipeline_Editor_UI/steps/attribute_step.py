from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_StepNode import PipelineStepNode #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_conf import registerPipelineStep #type: ignore

OPERATIONCODE_ATTRIBUTESTEP = 3

@registerPipelineStep(OPERATIONCODE_ATTRIBUTESTEP)
class AttributeStep(PipelineStepNode):
    """Proxies each assigned attribute onto its control.

    Has to run after the Control Rig step: the controls it proxies onto are
    created by that build, and the component attributes it reads from are created
    with them. Placing it earlier in the graph will report the controls as
    missing rather than silently doing nothing.
    """

    operation_code = OPERATIONCODE_ATTRIBUTESTEP
    operation_title = "Attributes"
    icon = ""

    def runStep(self):
        attribute_tab = self.scene.attribute_tab
        if attribute_tab is None:
            return False, "No attribute tab available"

        if not attribute_tab.getGraphScene().nodes:
            return False, "Attribute graph is empty"

        return attribute_tab.onBuildAll()
