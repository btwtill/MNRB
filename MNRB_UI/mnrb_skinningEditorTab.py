from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_DeformList import SkinningEditorDeformList #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_Toolbar import SkinningEditorToolbar #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable import Serializable #type: ignore

class mnrb_SkinningEditorTab(QWidget, Serializable): 
    def __init__(self, node_editor, parent=None):
        QWidget.__init__(self, parent)
        Serializable.__init__(self)

        self.is_tab_widget = True
        self._deformer_list = None

        self.node_editor = node_editor
        self.initUI()

    @property
    def deformer_list(self):
        """
        Get the deformer list.

        :return: Deformer list.
        """
        return self._deformer_list
    @deformer_list.setter
    def deformer_list(self, value):
        """
        Set the deformer list.

        :param value: Deformer list.
        """
        self._deformer_list = value

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
    
    def onOpenFile(self, file_Path):
        return True
    
    def onSaveFile(self, file_Path):
        return True
    
    def setComponentDeformerList(self):
        self.deformer_list = "Test"

    def getComponentDeformerList(self):
        return self.deformer_list

    def activate(self):
        current_active_deformers = self.getComponentDeformerList()

        print(current_active_deformers)