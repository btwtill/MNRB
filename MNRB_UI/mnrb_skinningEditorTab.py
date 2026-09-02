from collections import OrderedDict
import json, os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_DeformList import SkinningEditorDeformList #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_Toolbar import SkinningEditorToolbar #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_Cluster import SkinningEditorCluster #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_ClusterList import SkinningEditorClusterList #type: ignore
from MNRB.ROSE_Data.rose_Editor_Serializable import Serializable #type: ignore

class mnrb_SkinningEditorTab(QWidget, Serializable):
    def __init__(self, node_editor, parent=None):
        QWidget.__init__(self, parent)
        Serializable.__init__(self)

        self.is_tab_widget = True
        self._deformer_dict = {}
        self.skin_clusters = []
        #captured from onOpenFile/onSaveFile below, so weight store/apply/remove
        #buttons on a component box have somewhere to read/write on demand instead
        #of only whenever the project is explicitly saved or opened
        self.weights_folder_path = None

        #mirrors NodeEditorScene's has_been_modified pattern (node_Editor_UI/node_Editor_Scene.py),
        #so the title bar's unsaved-changes star and the New/Open/Close "unsaved
        #changes" prompt both cover skin cluster edits too, not just the node graph
        self._has_been_modified = False
        self._has_been_modified_listeners = []

        #mirrors how the node graph's undo history triggers mnrb_editor.py's
        #updateEditMenu() (connectHistoryModifiedListenersCallback in initTabs) -
        #without this, action_delete's enabled state never gets re-evaluated for
        #skin cluster selection, so the Del shortcut silently does nothing whenever
        #it was last left disabled by a node-graph-scoped check
        self._selection_changed_listeners = []

        self.node_editor = node_editor
        self.initUI()

    def connectSelectionChangedListenerCallback(self, callback):
        self._selection_changed_listeners.append(callback)

    def notifySelectionChanged(self):
        for callback in self._selection_changed_listeners:
            callback()

    def getScene(self):
        return self.node_editor.central_widget.scene

    @property
    def has_been_modified(self):
        return self._has_been_modified
    @has_been_modified.setter
    def has_been_modified(self, value):
        self._has_been_modified = value
        for callback in self._has_been_modified_listeners:
            callback()

    def setModified(self, state):
        self.has_been_modified = state

    def isModified(self):
        return self.has_been_modified

    def connectHasBeenModifiedListenerCallback(self, callback):
        self._has_been_modified_listeners.append(callback)

    @property
    def deformer_dict(self):
        return self._deformer_dict
    @deformer_dict.setter
    def deformer_dict(self, value):
        self._deformer_dict = value

        if not isinstance(self._deformer_dict, dict):
            self._deformer_dict = {}
            return

    def initUI(self):
        self.layout = QHBoxLayout(self)
        self.deformer_list = SkinningEditorDeformList(self.deformer_dict, self)

        self.layout.addWidget(self.deformer_list)
        
        self.cluster_layout = QVBoxLayout()
        self.skincluster_editor_toolbar = SkinningEditorToolbar(self)

        self.skincluster_object_list = SkinningEditorClusterList(self, self)

        self.cluster_layout.addWidget(self.skincluster_editor_toolbar)
        self.cluster_layout.addWidget(self.skincluster_object_list)

        self.layout.addLayout(self.cluster_layout)
    
    def loadFileFromPath(self, file_Path):
        if os.path.isdir(file_Path):
            graph_items = os.listdir(file_Path)

            #check if there is a graph in the current project directory if not create a new one
            if len(graph_items) >= 1:
                self.loadFile(os.path.join(file_Path, graph_items[0]))
            else:
                self.onNewFile()
        elif os.path.isfile(file_Path):
            self.loadFile(file_Path)
            
    def saveFileToPath(self, file_name):
        with open(file_name, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
        self.setModified(False)

    def onOpenFile(self, file_Path):
        #file_Path here is the project's mnrb_skinning_editor folder itself (see
        #mnrb_editor.py's onOpenProject), which is exactly the folder weight files
        #belong under
        self.weights_folder_path = file_Path
        self.loadFileFromPath(file_Path)
        return True

    def onSaveFile(self, file_name):
        self.weights_folder_path = os.path.dirname(file_name)
        self.saveFileToPath(file_name)
        return True

    def onNewFile(self):
        fake_data = OrderedDict([
            ('id', 0),
            ('deformer_dict', {})
        ])
        self.deserialize(fake_data, restore_id=False)

    def loadFile(self, file_Path):
        try:
            with open(file_Path, "r") as file:
                        raw_data = file.read()
                        data = json.loads(raw_data)
                        self.deserialize(data)

        except Exception as e:
                print(f"Error loading file: {e}")
                return False
        return True

    def setComponentDeformerDict(self, value):
        self.deformer_dict = value

    def getComponentDeformerDict(self):
        return self.deformer_dict

    def pullDeformerDictFromNodeEditor(self):
        self.deformer_dict = self.node_editor.getDeformerDict()

    def update_deformer_dict(self):
        new_dictionary = self.node_editor.getDeformerDict()
        self.setComponentDeformerDict(new_dictionary)
        self.deformer_list.updateDeformerList(new_dictionary)
        #component boxes highlight their own stale deform refs in red - that's only
        #meaningful to recompute once we actually know the current graph state
        self.skincluster_object_list.refreshAll()
        self.updateRemoveDeprecatedButtonState()
        self.updateAcceptNewButtonState()

    def activate(self):
        self.update_deformer_dict()

    def updateAcceptNewButtonState(self):
        self.skincluster_editor_toolbar.accept_new_deformers.setEnabled(self.deformer_list.hasNewEntries())

    def updateRemoveDeprecatedButtonState(self):
        #the deform list's own tracking only catches a removal it was actually
        #around to observe (i.e. since the last time this tab was activated) -
        #getAffectedSkinClusters() resolves live against the current scene every
        #time, so it stays correct even when the list's tracking lags behind
        has_deprecated = self.deformer_list.hasDeprecatedEntries() or len(self.getAffectedSkinClusters()) > 0
        self.skincluster_editor_toolbar.remove_deprecated_deformers.setEnabled(has_deprecated)

    #the Edit menu (mnrb_editor.py:updateEditMenu) generically calls these on
    #whichever tab is active - only Delete is meaningfully supported here, the
    #rest report unavailable rather than the AttributeError this used to throw
    #whenever the Edit menu was opened while the Skin tab was active
    def canCut(self):
        return False

    def canCopy(self):
        return False

    def canUndo(self):
        return False

    def canRedo(self):
        return False

    def canMirrorNode(self):
        return False

    def canDelete(self):
        return len(self.getSelectedSkinClusters()) > 0

    def onDelete(self):
        self.removeSelectedSkinClusters()
        self.skincluster_object_list.rebuild()

    def addSkinCluster(self, cluster_name):
        new_cluster = SkinningEditorCluster(self)
        new_cluster.cluster_name = cluster_name
        self.skin_clusters.append(new_cluster)
        self.setModified(True)
        return new_cluster

    def selectAllSkinClusters(self):
        for skin_cluster in self.skin_clusters:
            skin_cluster.is_selected = True

    def deselectAllSkinClusters(self):
        for skin_cluster in self.skin_clusters:
            skin_cluster.is_selected = False

    def getSelectedSkinClusters(self):
        return [skin_cluster for skin_cluster in self.skin_clusters if skin_cluster.is_selected]

    def removeAllSkinClusters(self):
        if self.skin_clusters:
            self.setModified(True)
        self.skin_clusters = []

    def removeSelectedSkinClusters(self):
        remaining = [skin_cluster for skin_cluster in self.skin_clusters if not skin_cluster.is_selected]
        if len(remaining) != len(self.skin_clusters):
            self.setModified(True)
        self.skin_clusters = remaining

    def buildAllSkinClusters(self, weights_folder = None):
        weights_folder = weights_folder if weights_folder is not None else self.weights_folder_path
        results = {skin_cluster: skin_cluster.build(self.getScene(), weights_folder) for skin_cluster in self.skin_clusters}
        if any(success for success, _ in results.values()):
            self.setModified(True)
        return results

    def buildSelectedSkinClusters(self, weights_folder = None):
        weights_folder = weights_folder if weights_folder is not None else self.weights_folder_path
        results = {skin_cluster: skin_cluster.build(self.getScene(), weights_folder) for skin_cluster in self.getSelectedSkinClusters()}
        if any(success for success, _ in results.values()):
            self.setModified(True)
        return results

    def getAffectedSkinClusters(self):
        #skinClusters referencing a deform that no longer resolves - the hook the
        #future diff-view UI checks to know what needs an Accept Changes pass
        scene = self.getScene()
        return [skin_cluster for skin_cluster in self.skin_clusters if skin_cluster.hasStaleRefs(scene)]

    def serialize(self):
        skin_clusters = [skin_cluster.serialize() for skin_cluster in self.skin_clusters]

        serialized_data = OrderedDict([
            ('id', self.id),
            ('deformer_dict', self.deformer_dict),
            #without this, tracked_dict (added/removed highlighting) resets to
            #empty every time the project is reopened, and the very first sync
            #after opening would show every existing deform as "newly added"
            ('tracked_deform_status', self.deformer_list.tracked_dict),
            ('skin_clusters', skin_clusters)
        ])
        return serialized_data

    def deserialize(self, data, hashmap={}, restore_id = True):
        if restore_id: self.id = data['id']
        print("SkinningEditorTab: Deserializing data: data['deformer_dict']")
        if 'deformer_dict' in data:
            self.setComponentDeformerDict(data['deformer_dict'])

        self.deformer_list.tracked_dict = data.get('tracked_deform_status', {})
        self.deformer_list.clear()
        self.deformer_list.initUI()

        self.skin_clusters = []
        for skin_cluster_data in data.get('skin_clusters', []):
            new_cluster = SkinningEditorCluster(self)
            new_cluster.deserialize(skin_cluster_data, hashmap, restore_id)
            self.skin_clusters.append(new_cluster)

        self.skincluster_object_list.rebuild()
        self.updateRemoveDeprecatedButtonState()
        self.updateAcceptNewButtonState()
        self.setModified(False)