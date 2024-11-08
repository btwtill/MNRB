from PySide2 import QtWidgets # type: ignore
from PySide2.QtCore import Qt # type: ignore

class NodeEditor_QGraphicContent(QtWidgets.QWidget):
    def __init__(self, node, parent=None):
        super().__init__(parent)

        self.node = node

        self.initUI()

    def initUI(self):

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.widget_label = QtWidgets.QLabel("Some Title")
        self.layout.addWidget(self.widget_label)
