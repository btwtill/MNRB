from collections import OrderedDict
import json, os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_DeformList import SkinningEditorDeformList #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_Toolbar import SkinningEditorToolbar #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_Cluster import SkinningEditorCluster #type: ignore
from MNRB.ROSE_Data.rose_Editor_Serializable import Serializable #type: ignore

class mnrb_SkinningEditorTab(QWidget, Serializable):
    def __init__(self, node_editor, parent=None):
        QWidget.__init__(self, parent)
        Serializable.__init__(self)

        self.is_tab_widget = True
        self._deformer_dict = {}
        self.skin_clusters = []

        self.node_editor = node_editor
        self.initUI()

    def getScene(self):
        return self.node_editor.central_widget.scene

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

        self.skincluster_object_list = QLabel("List of all Skincluters")

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

    def onOpenFile(self, file_Path):
        self.loadFileFromPath(file_Path)
        return True
    
    def onSaveFile(self, file_name):
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

    def activate(self):
        self.update_deformer_dict()

    def addSkinCluster(self, cluster_name):
        new_cluster = SkinningEditorCluster(self)
        new_cluster.cluster_name = cluster_name
        self.skin_clusters.append(new_cluster)
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
        self.skin_clusters = []

    def removeSelectedSkinClusters(self):
        self.skin_clusters = [skin_cluster for skin_cluster in self.skin_clusters if not skin_cluster.is_selected]

    def buildAllSkinClusters(self, weights_folder = None):
        return {skin_cluster: skin_cluster.build(self.getScene(), weights_folder) for skin_cluster in self.skin_clusters}

    def buildSelectedSkinClusters(self, weights_folder = None):
        return {skin_cluster: skin_cluster.build(self.getScene(), weights_folder) for skin_cluster in self.getSelectedSkinClusters()}

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
            ('skin_clusters', skin_clusters)
        ])
        return serialized_data

    def deserialize(self, data, hashmap={}, restore_id = True):
        if restore_id: self.id = data['id']
        print("SkinningEditorTab: Deserializing data: data['deformer_dict']")
        if 'deformer_dict' in data:
            self.setComponentDeformerDict(data['deformer_dict'])

        self.skin_clusters = []
        for skin_cluster_data in data.get('skin_clusters', []):
            new_cluster = SkinningEditorCluster(self)
            new_cluster.deserialize(skin_cluster_data, hashmap, restore_id)
            self.skin_clusters.append(new_cluster)