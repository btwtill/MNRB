from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_DeformList import SkinningEditorDeformList #type: ignore

class mnrb_SkinningEditorTab(QWidget): 
    def __init__(self, node_editor, parent=None):
        super().__init__(parent)

        self.node_editor = node_editor
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout(self)
        self.deformer_list = SkinningEditorDeformList(self)

        self.layout.addWidget(self.deformer_list)
        
        self.cluster_layout = QVBoxLayout()

        self.skincluster_editor_toolbar = QLabel("Toolbar for the Skin Clusters")
        self.skincluster_object_list = QLabel("List of all Skincluters")

        self.cluster_layout.addWidget(self.skincluster_editor_toolbar)
        self.cluster_layout.addWidget(self.skincluster_object_list)

        self.layout.addLayout(self.cluster_layout)

    def getComponentDeformerList(self):
        component_list = self.node_editor.getAllActiveComponents()
        return True
    
    def onOpenFile(self, file_Path):
        return True
    
    def onSaveFile(self, file_Path):
        return True