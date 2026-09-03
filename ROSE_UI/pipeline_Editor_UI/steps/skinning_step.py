from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_StepNode import PipelineStepNode #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_conf import registerPipelineStep #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.steps.output_path_step import OutputPathStep #type: ignore
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore

OPERATIONCODE_SKINNINGSTEP = 1

@registerPipelineStep(OPERATIONCODE_SKINNINGSTEP)
class SkinningStep(PipelineStepNode):
    operation_code = OPERATIONCODE_SKINNINGSTEP
    operation_title = "Skinning"
    icon = ""

    def __init__(self, scene):
        super().__init__(scene)
        #(mesh, original_parent_or_None) for every mesh moved by this run -
        #consumed and cleared by revertStep()
        self._reparent_actions = []

    def runStep(self):
        skinning_tab = self.scene.skinning_tab
        if skinning_tab is None:
            return False, "No skinning tab available"

        if not skinning_tab.skin_clusters:
            return False, "No skinClusters defined"

        results = skinning_tab.buildAllSkinClusters()

        failures = [skin_cluster.cluster_name for skin_cluster, (success, _) in results.items() if not success]

        #the mesh reorganization only serves a clean export - skip it unless an
        #enabled Output Path step is actually part of this run, so a plain
        #Build Full Pipeline (no export intended) just runs each step's build
        #like each tab's own "build all" would, nothing extra
        if self.hasEnabledOutputPathStep():
            self.moveSkinnedMeshesUnderGeometryHierarchy(results.keys())

        if failures:
            return False, "Failed: %s" % ", ".join(failures)

        return True, "Built %d skinCluster(s)" % len(results)

    def hasEnabledOutputPathStep(self):
        return any(
            isinstance(node, OutputPathStep) and not node.properties.is_disabled
            for node in self.scene.nodes
        )

    def moveSkinnedMeshesUnderGeometryHierarchy(self, skin_clusters):
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
            original_parent = current_parent[0] if current_parent else None
            if original_parent == geometry_group:
                continue
            MC.parentObject(mesh, geometry_group)
            self._reparent_actions.append((mesh, original_parent))

    def revertStep(self):
        #reverse order so a mesh that was reparented under another mesh that
        #also moved this run gets its original parent restored before that
        #parent itself moves back
        for mesh, original_parent in reversed(self._reparent_actions):
            if not MC.objectExists(mesh):
                continue
            if original_parent is not None and MC.objectExists(original_parent):
                MC.parentObject(mesh, original_parent)
            else:
                MC.unparentObject(mesh)

        self._reparent_actions = []
