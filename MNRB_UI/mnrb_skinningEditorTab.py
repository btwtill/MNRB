from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel #type: ignore

class mnrb_SkinningEditorTab(QWidget): 
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout(self)

        self.layout.addWidget(QLabel("Component Deformer List"))
        
        self.cluster_layout = QVBoxLayout()

        self.skincluster_editor_toolbar = QLabel("Toolbar for the Skin Clusters")
        self.skincluster_object_list = QLabel("List of all Skincluters")

        self.cluster_layout.addWidget(self.skincluster_editor_toolbar)
        self.cluster_layout.addWidget(self.skincluster_object_list)

        self.layout.addLayout(self.cluster_layout)
