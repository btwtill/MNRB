from PySide2 import QtWidgets # type: ignore
from PySide2.QtCore import Qt # type: ignore

class NodeEditor_QGraphicView(QtWidgets.QGraphicsView):
    def __init__(self, grScene, parent=None):
        super().__init__(parent)

        self.grScene = grScene
        
        self.setScene = self.grScene

        self.centerOn(0, 0)

        self.initUI()

    def initUI(self):

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F:
            self.centerOn(0, 0)