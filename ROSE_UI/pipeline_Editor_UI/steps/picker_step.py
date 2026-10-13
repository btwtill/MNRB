from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_StepNode import PipelineStepNode #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_conf import registerPipelineStep #type: ignore

OPERATIONCODE_PICKERSTEP = 5
#the Output Path step's, read here rather than imported: steps load in no fixed
#order, and a plain int compares across reloads where a class would not
OPERATIONCODE_OUTPUTPATHSTEP = 2


@registerPipelineStep(OPERATIONCODE_PICKERSTEP)
class PickerStep(PipelineStepNode):
    """Writes the Picker tab's picker as a script next to the exported rig.

    The animator runs that one file in Maya's Script Editor - it needs nothing
    else installed - picks the rig's namespace, and has the picker. It goes to
    the Output Path step's directory, so the rig and its picker ship together.
    """

    operation_code = OPERATIONCODE_PICKERSTEP
    operation_title = "Picker"
    icon = ""

    def runStep(self):
        picker_tab = getattr(self.scene, "picker_tab", None)
        if picker_tab is None:
            return False, "No picker tab available"

        directories = [node.properties.output_directory for node in self.scene.nodes
                       if getattr(node, "operation_code", None) == OPERATIONCODE_OUTPUTPATHSTEP
                       and getattr(node.properties, "output_directory", "")]
        if not directories:
            return False, "No output directory - set one on the Output Path step"

        import os
        os.makedirs(directories[0], exist_ok = True)
        return picker_tab.exportPicker(directories[0])
