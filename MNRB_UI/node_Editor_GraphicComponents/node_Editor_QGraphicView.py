from PySide2 import QtWidgets # type: ignore
from PySide2.QtCore import Qt, QEvent # type: ignore
from PySide2.QtGui import QPainter, QMouseEvent # type:ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore

CLASS_DEBUG = False

class NodeEditor_QGraphicView(QtWidgets.QGraphicsView):
    def __init__(self, grScene, parent=None):
        super().__init__(parent)

        self.grScene = grScene
        self.setScene = self.grScene

        self.initUI()

        self.centerOn(0, 0)

    def initUI(self) -> None:

        #zoom Properties
        self.clamp_Zoom = True
        self.zoomIn_Factor = 1.25
        self.zoom = 10
        self.zoom_Step = 1
        self.zoomRange = [1, 20]

        #set scroll Bar Policies
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        #Set Render Attributes
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

    def mousePressEvent(self, event) -> None:
        #decide what button has been pressed and execute the according action
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.LeftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.RightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        #decide what button has been Released and execute the according action
        if event.button() == Qt.MiddleButton :
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.LeftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.RightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event) -> None:
        #center view
        if event.key() == Qt.Key_F:
            self.centerOn(0, 0)
        if event.key() == Qt.Key_N:
            newNode = NodeEditorNode(self.grScene.scene, title="TestNode", inputs = [1], outputs=[1, 1])

    def middleMouseButtonPress(self, event) -> None:
        if CLASS_DEBUG: print("GRAPHICSVIEW:: --middleMouseButtonPress:: Middle Mouse Button Press Start")

        #fake the middle mouse button release
        fake_releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(), Qt.MiddleButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(fake_releaseEvent)

        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

        #fake left mouse Button Press
        fake_leftMousePress_Event = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fake_leftMousePress_Event)

    
    def middleMouseButtonRelease(self, event):
        if CLASS_DEBUG: print("GRAPHICSVIEW:: --middleMouseButtonRelease:: Middle Mouse Button Release Start")

        #fake left mouse button Release
        fake_left_MouseRelease_Event = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | ~Qt.MouseButton.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fake_left_MouseRelease_Event)

        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    def LeftMouseButtonPress(self, event):
        return super().mousePressEvent(event)

    def RightMouseButtonPress(self, event):
        return super().mousePressEvent(event)
    
    def LeftMouseButtonRelease(self, event):
        return super().mouseReleaseEvent(event)
    
    def RightMouseButtonRelease(self, event):
        return super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        if CLASS_DEBUG : print("GRAPHICSVIEW:: --wheelEvent:: Starting WheelEvent")

        zoomOutFactor = 1 / self.zoomIn_Factor

        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomIn_Factor
            self.zoom += self.zoom_Step
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoom_Step
        
        clamped = False
        if self.zoom < self.zoomRange[0]:  self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]:  self.zoom, clamped = self.zoomRange[1], True

        if not clamped or self.clamp_Zoom is False:
            self.scale(zoomFactor, zoomFactor)
        