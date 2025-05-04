from PySide2.QtWidgets import QWidget, QSizePolicy, QHBoxLayout, QPushButton # type: ignore
from PySide2.QtCore import QSize # type: ignore

class SkinningEditorToolbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.layout = QHBoxLayout(self)
        test_button = QPushButton("Add new SkinCluster")
        test_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        self.layout.addWidget(test_button)

    def sizeHint(self):
        return QSize(200, 50)