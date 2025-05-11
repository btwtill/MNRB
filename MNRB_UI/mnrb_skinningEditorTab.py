from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_DeformList import SkinningEditorDeformList #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_Toolbar import SkinningEditorToolbar #type: ignore

class mnrb_SkinningEditorTab(QWidget): 
    def __init__(self, node_editor, parent=None):
        super().__init__(parent)
        self.is_tab_widget = True

        self.node_editor = node_editor
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout(self)
        self.deformer_list = SkinningEditorDeformList(self)

        self.layout.addWidget(self.deformer_list)
        
        self.cluster_layout = QVBoxLayout()
        self.skincluster_editor_toolbar = SkinningEditorToolbar(self)

        self.skincluster_object_list = QLabel("List of all Skincluters")

        self.cluster_layout.addWidget(self.skincluster_editor_toolbar)
        self.cluster_layout.addWidget(self.skincluster_object_list)

        self.layout.addLayout(self.cluster_layout)

    def getComponentDeformerList(self):
        component_list = self.node_editor.getAllActiveComponents()
        return component_list
    
    def onOpenFile(self, file_Path):
        return True
    
    def onSaveFile(self, file_Path):
        return True
    
    def activate(self):
        current_active_deformers = self.getComponentDeformerList()

        print(current_active_deformers)