from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket import LEFT, RIGHT #type: ignore
from PySide2 import QtWidgets # type: ignore
from PySide2.QtCore import Qt # type: ignore


class NodeEditor_QGraphicContent(QtWidgets.QWidget):
    def __init__(self, node, parent=None):
        super().__init__(parent)

        self.node = node
        self.socket_labels = []

        self.initUI()

    def initUI(self):

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(3,0,3,0)
        self.layout.setSpacing(7)
        self.setLayout(self.layout)

    def addSocketLabel(self, value, alignment, position):
        new_socket_label = QtWidgets.QLabel(value)
        if alignment == RIGHT:
            new_socket_label.setAlignment(Qt.AlignRight)
        self.socket_labels.append(new_socket_label)
        self.layout.addWidget(new_socket_label)