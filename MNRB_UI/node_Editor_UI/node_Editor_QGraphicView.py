from PySide2 import QtWidgets # type: ignore
from PySide2.QtCore import Qt # type: ignore
from PySide2.QtGui import QPainter # type:ignore

CLASS_DEBUG = True

class NodeEditor_QGraphicView(QtWidgets.QGraphicsView):
    def __init__(self, grScene, parent=None):
        super().__init__(parent)

        self.grScene = grScene
        self.setScene = self.grScene

        self.initUI()

        self.centerOn(0, 0)

    def initUI(self):
        #set scroll Bar Policies
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        #Set Render Attributes
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

    def mousePressEvent(self, event):
        #decide what button has been pressed and execute the according action
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        #decide what button has been Released and execute the according action
        if event.button() == Qt.MiddleButton :
            self.middleMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):

        #center view
        if event.key() == Qt.Key_F:
            self.centerOn(0, 0)

    def middleMouseButtonPress(self, event):
        if CLASS_DEBUG: print("GRAPHICSVIEW:: --middleMouseButtonPress:: Middle Mouse Button Press Start")
    
    def middleMouseButtonRelease(self, event):
        if CLASS_DEBUG: print("GRAPHICSVIEW:: --middleMouseButtonRelease:: Middle Mouse Button Release Start")