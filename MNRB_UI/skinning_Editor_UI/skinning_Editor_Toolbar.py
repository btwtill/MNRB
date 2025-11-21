from PySide2.QtWidgets import QWidget, QSizePolicy, QHBoxLayout, QPushButton # type: ignore
from PySide2.QtCore import QSize, Qt # type: ignore

class SkinningEditorToolbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        self.setMaximumHeight(50)

        self.layout = QHBoxLayout(self)

        self.add_skincluster_button = QPushButton("New SkinCluster")
        
        self.remove_deprecated_deformers = QPushButton("remove Deprecated")
        self.remove_deprecated_deformers.setEnabled(False)

        self.layout.addWidget(self.add_skincluster_button, alignment=Qt.AlignLeft)
        self.layout.addWidget(self.remove_deprecated_deformers, alignment=Qt.AlignLeft)