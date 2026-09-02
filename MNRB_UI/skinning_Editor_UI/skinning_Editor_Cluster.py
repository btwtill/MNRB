import os
from collections import OrderedDict
from MNRB.ROSE_Data.rose_Editor_Serializable import Serializable #type: ignore
from MNRB.MNRB_naming.MNRB_names import MNRB_Names #type: ignore
from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

class SkinningEditorCluster(Serializable):
    """
    A user-defined grouping of deform joints bound to a single target mesh via one
    Maya skinCluster. Backend/data-model only - no UI wiring (drag-drop, buttons,
    diff view) happens here.
    """

    def __init__(self, tab):
        super().__init__()

        self.skinning_tab = tab

        self.cluster_name = "Untitled"
        #each entry is {"id": deform.id, "name": deform.name} - resolved back to a
        #live deform object on demand via resolveDeforms(), never stored as a direct
        #object reference (deforms get recreated on every static rebuild)
        self.deform_refs = []

        self.target_mesh = None
        self.auto_apply_weights = False

        #MNRB-tab-internal selection state, unrelated to Maya's viewport selection
        self.is_selected = False

        #set once build() actually creates a skinCluster node, so a rebuild deletes
        #and replaces it instead of accumulating duplicates
        self.maya_skin_cluster_node = None

        #name-set snapshot of the influences at the time weights were last exported -
        #compared against the current influence set to decide if a stored weights
        #file is still safe to reapply
        self._exported_influence_names = set()

    def addDeform(self, deform):
        if any(ref["id"] == deform.id for ref in self.deform_refs):
            return
        self.deform_refs.append({"id": deform.id, "name": deform.name})

    def removeDeform(self, deform_id):
        self.deform_refs = [ref for ref in self.deform_refs if ref["id"] != deform_id]

    def setTargetFromSelection(self):
        selection = MC.getViewportSelection()

        if len(selection) != 1:
            return False, "Select exactly one mesh to use as the skinCluster target"

        if not MC.objectIsMesh(selection[0]):
            return False, "'%s' is not a mesh" % selection[0]

        self.target_mesh = selection[0]
        return True, self.target_mesh

    def resolveDeforms(self, scene):
        """Resolve every stored deform reference against the live scene.

        Tries the stored id first (survives a component rename), and falls back to
        the stored name if the id no longer resolves (survives a static rebuild,
        which recreates deform objects with fresh ids but usually-identical names).
        A fallback match self-heals the stored id. Only a reference that resolves
        by neither id nor name is genuinely stale.

        Returns (resolved_deforms, unresolved_refs).
        """
        resolved_deforms = []
        unresolved_refs = []

        for ref in self.deform_refs:
            deform = scene.getDeformById(ref["id"])

            if deform is None:
                deform = scene.getDeformByName(ref["name"])
                if deform is not None:
                    ref["id"] = deform.id

            if deform is not None:
                resolved_deforms.append(deform)
            else:
                unresolved_refs.append(ref)

        return resolved_deforms, unresolved_refs

    def hasStaleRefs(self, scene):
        _, unresolved_refs = self.resolveDeforms(scene)
        return len(unresolved_refs) > 0

    def removeStaleRefs(self, scene):
        _, unresolved_refs = self.resolveDeforms(scene)
        stale_ids = set(ref["id"] for ref in unresolved_refs)
        self.deform_refs = [ref for ref in self.deform_refs if ref["id"] not in stale_ids]

    def getSkinClusterName(self):
        return self.cluster_name + MNRB_Names.skincluster_suffix

    def build(self, scene, weights_folder = None):
        if not self.target_mesh:
            return False, "No target mesh set"

        if not MC.objectExists(self.target_mesh):
            return False, "Target mesh '%s' does not exist" % self.target_mesh

        resolved_deforms, unresolved_refs = self.resolveDeforms(scene)
        existing_deforms = [deform for deform in resolved_deforms if deform.exists()]
        missing_deforms = [deform.name for deform in resolved_deforms if not deform.exists()]
        skipped = [ref["name"] for ref in unresolved_refs] + missing_deforms

        if not existing_deforms:
            return False, "No valid deforms to bind"

        if self.maya_skin_cluster_node and MC.objectExists(self.maya_skin_cluster_node):
            MC.deleteNode(self.maya_skin_cluster_node)

        joint_names = [deform.name for deform in existing_deforms]
        self.maya_skin_cluster_node = MC.createSkinCluster(joint_names, self.target_mesh, self.getSkinClusterName())

        if self.auto_apply_weights and weights_folder is not None and self.areWeightsValid():
            self.importWeights(weights_folder)

        return True, skipped

    def getWeightsFilePath(self, folder_path):
        #keyed by this container's stable id rather than its display name, so
        #renaming a container doesn't orphan its weights file
        return os.path.join(folder_path, "weights", "%s.xml" % self.id)

    def exportWeights(self, folder_path):
        if not self.maya_skin_cluster_node or not MC.objectExists(self.maya_skin_cluster_node):
            return False, "No built skinCluster to export weights from"

        if not self.target_mesh or not MC.objectExists(self.target_mesh):
            return False, "No valid target mesh"

        file_path = self.getWeightsFilePath(folder_path)
        MC.exportDeformerWeights(self.maya_skin_cluster_node, self.target_mesh, file_path)

        self._exported_influence_names = set(ref["name"] for ref in self.deform_refs)
        return True, file_path

    def importWeights(self, folder_path):
        file_path = self.getWeightsFilePath(folder_path)

        if not os.path.isfile(file_path):
            return False, "No stored weights file found for '%s'" % self.cluster_name

        if not self.maya_skin_cluster_node or not MC.objectExists(self.maya_skin_cluster_node):
            return False, "No built skinCluster to import weights onto"

        MC.importDeformerWeights(self.maya_skin_cluster_node, self.target_mesh, file_path)
        return True, file_path

    def areWeightsValid(self):
        if not self._exported_influence_names:
            return False
        current_names = set(ref["name"] for ref in self.deform_refs)
        return current_names == self._exported_influence_names

    def serialize(self):
        serialize_data = OrderedDict([
            ('id', self.id),
            ('cluster_name', self.cluster_name),
            ('deform_refs', self.deform_refs),
            ('target_mesh', self.target_mesh),
            ('auto_apply_weights', self.auto_apply_weights),
            ('maya_skin_cluster_node', self.maya_skin_cluster_node),
            ('exported_influence_names', list(self._exported_influence_names)),
        ])
        return serialize_data

    def deserialize(self, data, hashmap = {}, restore_id = True):
        if restore_id: self.id = data['id']

        self.cluster_name = data['cluster_name']
        self.deform_refs = data.get('deform_refs', [])
        self.target_mesh = data.get('target_mesh', None)
        self.auto_apply_weights = data.get('auto_apply_weights', False)
        self.maya_skin_cluster_node = data.get('maya_skin_cluster_node', None)
        self._exported_influence_names = set(data.get('exported_influence_names', []))

        return True
