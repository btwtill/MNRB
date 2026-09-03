from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_StepNode import PipelineStepNode #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_conf import registerPipelineStep #type: ignore
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore

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

        self.moveSkinnedMeshesUnderGeometryHierarchy(results.keys())

        if failures:
            return False, "Failed: %s" % ", ".join(failures)

        return True, "Built %d skinCluster(s)" % len(results)

    def moveSkinnedMeshesUnderGeometryHierarchy(self, skin_clusters):
        #the pipeline build is the only place this reorganization happens - it
        #keeps the exported rig clean (guides/helpers live outside the rig
        #hierarchy and are excluded from OutputPathStep's selection-based
        #export) without disturbing the scene while artists iterate on binds
        #directly from the Skinning tab
        node_editor_tab = self.scene.node_editor_tab
        if node_editor_tab is None:
            return

        target_meshes = set(
            skin_cluster.target_mesh for skin_cluster in skin_clusters
            if skin_cluster.target_mesh and MC.objectExists(skin_cluster.target_mesh)
        )
        if not target_meshes:
            return

        rig_scene = node_editor_tab.central_widget.scene
        virtual_rig_hierarchy = rig_scene.virtual_rig_hierarchy
        if not virtual_rig_hierarchy.rig_hierarchy_object.ensureExistence():
            return

        virtual_rig_hierarchy.geometry_hierarchy_object.ensureExistence()
        geometry_group = virtual_rig_hierarchy.geometry_hierarchy_object.name

        for mesh in target_meshes:
            current_parent = MC.getObjectParentNode(mesh)
            if current_parent and current_parent[0] == geometry_group:
                continue
            MC.parentObject(mesh, geometry_group)
