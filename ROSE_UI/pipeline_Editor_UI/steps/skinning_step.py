from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_StepNode import PipelineStepNode #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_conf import registerPipelineStep #type: ignore

OPERATIONCODE_SKINNINGSTEP = 1

@registerPipelineStep(OPERATIONCODE_SKINNINGSTEP)
class SkinningStep(PipelineStepNode):
    operation_code = OPERATIONCODE_SKINNINGSTEP
    operation_title = "Skinning"
    icon = ""

    def runStep(self):
        skinning_tab = self.scene.skinning_tab
        if skinning_tab is None:
            return False, "No skinning tab available"

        if not skinning_tab.skin_clusters:
            return False, "No skinClusters defined"

        results = skinning_tab.buildAllSkinClusters()

        failures = [skin_cluster.cluster_name for skin_cluster, (success, _) in results.items() if not success]

        if failures:
            return False, "Failed: %s" % ", ".join(failures)

        return True, "Built %d skinCluster(s)" % len(results)
