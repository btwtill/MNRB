import math
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
MOVE_DEBUG = False
WHEEL_DEBUG = False

MODE_NOOP = 1
MODE_EDGEDRAG = 2

EDGE_DRAG_START_THRESHOLD = 20

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
        self.zoom_content_visibility_threshold = 9
        self.clamp_zoom = True
        self.zoom_in_factor = 1.25
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = [1, 20]

        self.is_content_visible = False if self.zoom <= self.zoom_content_visibility_threshold else True

        self.centerOn(0, 0)

    def mousePressEvent(self, event) -> None:
        #decide what button has been pressed and execute the according action
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        #decide what button has been Released and execute the according action
        if event.button() == Qt.MiddleButton :
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
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

        item_on_relase_event = self.getItemAtEvent(event)

        if SCENE_DEBUG: 
            if isinstance(item_on_relase_event, NodeEditor_QGraphicSocket):
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: Item Clicked On:: ", item_on_relase_event.socket)
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: \thasEdges:: ")
                for edge in item_on_relase_event.socket.edges:
                    print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t\t", edge)
            elif isinstance(item_on_relase_event, NodeEditor_QGraphicEdge):
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: Item Clicked On:: ", item_on_relase_event)
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t\tConnecting Socket:: ", item_on_relase_event.edge.start_socket,"<---->", item_on_relase_event.edge.end_socket)
            else:
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: Item Clicked On:: ", item_on_relase_event)

        if SCENE_DEBUG and event.modifiers() == Qt.CTRL: 
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: Items in Scene:: ")
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: \tNodes:: ")
            for node in self.grScene.scene.nodes:
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t\t", node)
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: \tEdges:: ")
            for edge in self.grScene.scene.edges:
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t\t", edge)
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: Items in GraphicScene:: ")
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: \tGraphicNodes")
            for item in self.grScene.items():
                if isinstance(item, NodeEditor_QGraphicNode):
                    print("GRAPHICSVIEW:: --middleMouseButtonPress:: Graphic Node:: \t", item)
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: \tGraphicEdges")
            for item in self.grScene.items():
                if isinstance(item, NodeEditor_QGraphicEdge):
                    print("GRAPHICSVIEW:: --middleMouseButtonPress:: Graphic Edge:: \t", item)
            
    def leftMouseButtonPress(self, event):

        item_on_click = self.getItemAtEvent(event)
        self.last_mouse_button_press_position = self.mapToScene(event.pos())

        if isinstance(item_on_click, NodeEditor_QGraphicSocket):
            if EVENT_DEBUG: print("GRAPHICSVIEW:: --leftMouseButtonPress:: Socket Detected")
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGEDRAG
                self.dragging_edge.startEdgeDrag(item_on_click)
                return
        
        if self.mode == MODE_EDGEDRAG:
            self.mode = MODE_NOOP
            drag_result = self.dragging_edge.endEdgeDrag(item_on_click)
            if drag_result: return

        super().mousePressEvent(event)

    def rightMouseButtonPress(self, event):
        return super().mousePressEvent(event)
    
    def leftMouseButtonRelease(self, event):

        item_on_release = self.getItemAtEvent(event)

        if self.getDistanceFromLastLeftMousePressEvent(event) > math.pow(EDGE_DRAG_START_THRESHOLD, 2):
            if self.mode == MODE_EDGEDRAG:
                self.mode = MODE_NOOP
                drag_result = self.dragging_edge.endEdgeDrag(item_on_release)
                if drag_result: return

        return super().mouseReleaseEvent(event)
    
    def rightMouseButtonRelease(self, event):
        return super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):

        event_mouse_position = self.mapToScene(event.pos())

        if MOVE_DEBUG: print("GRAPHICSVIEW:: --mouseMoveEvent:: ", self.mode)
        if MOVE_DEBUG: print("GRAPHICSVIEW:: --mouseMoveEvent:: is EdgeDrag:: ", self.mode == MODE_EDGEDRAG)
        if MOVE_DEBUG: print("GRAPHICSVIEW:: --mouseMoveEvent:: MODE_EDGE_DRAG ", MODE_EDGEDRAG)

        if self.mode == MODE_EDGEDRAG:
            self.dragging_edge.updateDestination(event_mouse_position.x(), event_mouse_position.y())

        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        if WHEEL_DEBUG : print("GRAPHICSVIEW:: --wheelEvent:: Starting WheelEvent")

        zoomOutFactor = 1 / self.zoom_in_factor

        if event.angleDelta().y() > 0:
            zoomFactor = self.zoom_in_factor
            self.zoom += self.zoom_step
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoom_step
        
        clamped = False
        if self.zoom < self.zoom_range[0]:  self.zoom, clamped = self.zoom_range[0], True
        if self.zoom > self.zoom_range[1]:  self.zoom, clamped = self.zoom_range[1], True

        if not clamped or self.clamp_zoom is False:
            self.scale(zoomFactor, zoomFactor)

        #Set Visibility of the nodes content depending on the zoom Level
        if self.zoom <= self.zoom_content_visibility_threshold:
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
        return self.itemAt(event.pos())
    
    def getDistanceFromLastLeftMousePressEvent(self, event):
        current_event_scene_position = self.mapToScene(event.pos())
        distance_to_last_left_mouse_press = current_event_scene_position - self.last_mouse_button_press_position

        return math.pow(distance_to_last_left_mouse_press.x(), 2) + math.pow(distance_to_last_left_mouse_press.y(), 2)