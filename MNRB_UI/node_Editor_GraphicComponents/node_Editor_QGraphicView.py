from PySide2 import QtWidgets # type: ignore
from PySide2.QtCore import Qt, QEvent # type: ignore
from PySide2.QtGui import QPainter, QMouseEvent # type:ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node import NodeEditorNode #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_DragEdge import NodeEditorDragEdge #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicSocket import NodeEditor_QGraphicSocket #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicNode import NodeEditor_QGraphicNode #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge import NodeEditor_QGraphicEdge #type: ignore

EVENT_DEBUG = True
CLASS_DEBUG = False
SCENE_DEBUG = True

MODE_NOOP = 1
MODE_EDGEDRAG = 2

class NodeEditor_QGraphicView(QtWidgets.QGraphicsView):
    def __init__(self, grScene, parent=None):
        super().__init__(parent)

        print(parent)
        print(grScene)

        self.grScene = grScene

        self.initViewItems()
        self.initViewStates()
        self.initUI()

    def initViewItems(self):
        self.dragging_edge = NodeEditorDragEdge(self)

    def initViewStates(self):
        self.mode = MODE_NOOP

    def initUI(self) -> None:
        #Set Render Attributes
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

        #set scroll Bar Policies
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        self.setScene(self.grScene)

        #zoom Properties
        self.clamp_Zoom = True
        self.zoomIn_Factor = 1.25
        self.zoom = 10
        self.zoom_Step = 1
        self.zoomRange = [1, 20]

        self.is_content_visible = False if self.zoom <= 9 else True

        self.centerOn(0, 0)

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
            newNode = NodeEditorNode(self.grScene.scene, title="TestNode", inputs = [["input",1], ["input", 1]], outputs=[["output",1], ["output", 1], ["output",1]])

    def middleMouseButtonPress(self, event) -> None:
        if EVENT_DEBUG: print("GRAPHICSVIEW:: --middleMouseButtonPress:: Middle Mouse Button Press Start")

        #fake the middle mouse button release
        fake_releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(), Qt.MiddleButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(fake_releaseEvent)

        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

        #fake left mouse Button Press
        fake_leftMousePress_Event = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fake_leftMousePress_Event)

    
    def middleMouseButtonRelease(self, event):
        if EVENT_DEBUG: print("GRAPHICSVIEW:: --middleMouseButtonRelease:: Middle Mouse Button Release Start")

        #fake left mouse button Release
        fake_left_MouseRelease_Event = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | ~Qt.MouseButton.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fake_left_MouseRelease_Event)

        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

        if SCENE_DEBUG: print("GRAPHICSVIEW:: --MiddleMouseButtonPress:: Item Clicked On:: ", self.getItemAtEvent(event))
        if SCENE_DEBUG and event.modifiers() == Qt.CTRL: 
            print("GRAPHICSVIEW:: --MiddleMouseButtonPress:: Items in Scene:: ")
            print("GRAPHICSVIEW:: --MiddleMouseButtonPress:: \tNodes:: ")
            for node in self.grScene.scene.nodes:
                print("GRAPHICSVIEW:: --MiddleMouseButtonPress:: \t\t", node)
            print("GRAPHICSVIEW:: --MiddleMouseButtonPress:: \tEdges:: ")
            for edge in self.grScene.scene.edges:
                print("GRAPHICSVIEW:: --MiddleMouseButtonPress:: \t\t", edge)
            print("GRAPHICSVIEW:: --MiddleMouseButtonPress:: Items in GraphicScene:: ")
            print("GRAPHICSVIEW:: --MiddleMouseButtonPress:: \tGraphicNodes")
            for item in self.grScene.items():
                if isinstance(item, NodeEditor_QGraphicNode):
                    print("GRAPHICSVIEW:: --MiddleMouseButtonPress:: Graphic Node:: \t", item)
            print("GRAPHICSVIEW:: --MiddleMouseButtonPress:: \tGraphicEdges")
            for item in self.grScene.items():
                if isinstance(item, NodeEditor_QGraphicEdge):
                    print("GRAPHICSVIEW:: --MiddleMouseButtonPress:: Graphic Edge:: \t", item)
            
    def LeftMouseButtonPress(self, event):

        item_on_click = self.getItemAtEvent(event)

        if isinstance(item_on_click, NodeEditor_QGraphicSocket):
            if EVENT_DEBUG: print("GRAPHICSVIEW:: --LeftMouseButtonPress:: Socket Detected")
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGEDRAG
                self.dragging_edge.startEdgeDrag(item_on_click)
                return
        
        if self.mode == MODE_EDGEDRAG:
            self.mode = MODE_NOOP
            drag_result = self.dragging_edge.endEdgeDrag(item_on_click)
            if drag_result: return

        super().mousePressEvent(event)

    def RightMouseButtonPress(self, event):
        return super().mousePressEvent(event)
    
    def LeftMouseButtonRelease(self, event):

        item_on_release = self.getItemAtEvent(event)

        if self.mode == MODE_EDGEDRAG:
            self.mode = MODE_NOOP
            drag_result = self.dragging_edge.endEdgeDrag(item_on_release)
            if drag_result: return

        return super().mouseReleaseEvent(event)
    
    def RightMouseButtonRelease(self, event):
        return super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        if EVENT_DEBUG : print("GRAPHICSVIEW:: --wheelEvent:: Starting WheelEvent")

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

        #Set Visibility of the nodes content depending on the zoom Level
        if self.zoom <= 9:
            if self.is_content_visible:
                for node in self.grScene.scene.nodes:
                    node.content.hide()
            self.is_content_visible = False
        else:
            if not self.is_content_visible:
                for node in self.grScene.scene.nodes:
                    node.content.show()
            self.is_content_visible = True
        
    def getItemAtEvent(self, event):
        position = event.pos()
        object = self.itemAt(position)
        return object