from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_DeformList import SkinningEditorDeformList #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_Toolbar import SkinningEditorToolbar #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore

class mnrb_SkinningEditorTab(QWidget, Serializable): 
    def __init__(self, node_editor, parent=None):
        QWidget.__init__(self, parent)
        Serializable.__init__(self)

        self.is_tab_widget = True
        self._deformer_dict = None

        self.node_editor = node_editor
        self.initUI()

    @property
    def deformer_dict(self):
        return self._deformer_dict
    @deformer_dict.setter
    def deformer_dict(self, value):
        self._deformer_dict = value

    def initUI(self):
        self.layout = QHBoxLayout(self)
        self.deformer_dict = SkinningEditorDeformList(self)

        self.layout.addWidget(self.deformer_dict)
        
        self.cluster_layout = QVBoxLayout()
        self.skincluster_editor_toolbar = SkinningEditorToolbar(self)

        self.skincluster_object_list = QLabel("List of all Skincluters")

        self.cluster_layout.addWidget(self.skincluster_editor_toolbar)
        self.cluster_layout.addWidget(self.skincluster_object_list)

        self.layout.addLayout(self.cluster_layout)
    
    def onOpenFile(self, file_Path):
        return True
    
    def onSaveFile(self, file_Path):
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

    def activate(self):
        self.update_deformer_dict()