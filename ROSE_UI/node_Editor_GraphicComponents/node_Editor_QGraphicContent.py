from PySide6 import QtWidgets # type: ignore
from PySide6.QtCore import Qt # type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_Socket import LEFT, RIGHT #type: ignore

class NodeEditor_QGraphicContent(QtWidgets.QWidget):
    def __init__(self, node, parent=None):
        super().__init__(parent)

        self.node = node
        self.socket_labels = []
        self.initUI()

    def initUI(self):

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(3,0,3,0)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)

        if self.node.scene.getView().zoom <= self.node.scene.getView().zoom_content_visibility_threshold:
            self.hide()

    def addSocketLabel(self, value, alignment, position):
        new_socket_label = QtWidgets.QLabel(value)
        new_socket_label.node = self.node
        new_socket_label_font = new_socket_label.font()
        new_socket_label_font.setPointSize(7)
        new_socket_label.setFont(new_socket_label_font)

        if alignment == RIGHT:
            new_socket_label.setAlignment(Qt.AlignCenter)
        else:
            new_socket_label.setAlignment(Qt.AlignCenter)

        #parented directly rather than put in the layout: the labels are placed to
        #match their sockets (see alignLabelsToSockets), and a layout distributing
        #them on its own would just fight that
        new_socket_label.setParent(self)
        new_socket_label.show()

        self.socket_labels.append(new_socket_label)
        
    def alignLabelsToSockets(self, socket_label_pairs, title_height, edge_padding, content_width):
        """Put each label's vertical centre on its socket's y.

        This direction round on purpose. The sockets are spaced to stay easy to
        see and to click, so the text follows them - driving it the other way
        moved the sockets onto the label positions and made them noticeably
        harder to hit.
        """
        for socket, label in socket_label_pairs:
            if not label.isVisible():
                continue

            graphic_socket = getattr(socket, "grSocket", None)
            if graphic_socket is None:
                continue

            label_height = label.sizeHint().height()
            #socket y is in graphics-node coordinates, and this widget starts
            #below the title bar, so shift into the content widget's own space
            local_y = graphic_socket.pos().y() - (title_height + edge_padding) - label_height / 2.0

            label.setGeometry(0, int(round(local_y)), int(content_width), int(label_height))

    def getContentLabels(self):
        return self.socket_labels
    
    def removeLastLabel(self):

        last_label = self.socket_labels.pop()

        last_label.setParent(None)
        last_label.deleteLater()

        self.updateGeometry()

    def __str__(self): return "ClassInstance::%s::  %s..%s" % (__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])