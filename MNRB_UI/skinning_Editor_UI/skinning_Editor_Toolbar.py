from PySide2.QtWidgets import QWidget, QSizePolicy, QHBoxLayout, QPushButton # type: ignore
from PySide2.QtCore import QSize, Qt # type: ignore

class SkinningEditorToolbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        self.setMaximumHeight(50)

        self.layout = QHBoxLayout(self)

        test_button = QPushButton("Add new SkinCluster")
        test_button.setMaximumWidth(200)

        self.layout.addWidget(test_button, alignment=Qt.AlignLeft)