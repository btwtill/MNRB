from MNRB.MNRB_UI.pipeline_Editor_UI.pipeline_Editor_StepNode import PipelineStepNode #type: ignore
from MNRB.MNRB_UI.pipeline_Editor_UI.pipeline_Editor_conf import registerPipelineStep #type: ignore

OPERATIONCODE_CONTROLRIGSTEP = 0

@registerPipelineStep(OPERATIONCODE_CONTROLRIGSTEP)
class ControlRigStep(PipelineStepNode):
    operation_code = OPERATIONCODE_CONTROLRIGSTEP
    operation_title = "Control Rig"
    icon = ""

    def runStep(self):
        node_editor_tab = self.scene.node_editor_tab
        if node_editor_tab is None:
            return False, "No node editor tab available"

        rig_scene = node_editor_tab.central_widget.scene

        if not rig_scene.nodes:
            return False, "Node graph is empty"

        try:
            rig_scene.buildSceneGuides()
            rig_scene.buildSceneStatic()
            rig_scene.buildSceneComponents()
            rig_scene.connectSceneComponents()
        except Exception as e:
            return False, "Control rig build failed: %s" % e

        return True, "Built"
