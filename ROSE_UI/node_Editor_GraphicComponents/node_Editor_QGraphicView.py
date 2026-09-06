import math
from PySide6 import QtWidgets # type: ignore
from PySide6.QtCore import Qt, QEvent, Signal, QPoint, QRect, QRectF, QPointF # type: ignore
from PySide6.QtGui import QPainter, QMouseEvent, QPen, QColor # type:ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_DragEdge import NodeEditorDragEdge #type: ignore
from MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicSocket import NodeEditor_QGraphicSocket, NodeEditor_QGraphicCollapsedSocket #type: ignore
from MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicNode import NodeEditor_QGraphicNode #type: ignore
from MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge import NodeEditor_QGraphicEdge #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_Cutline import NodeEditorCutLine #type: ignore
from MNRB.ROSE_UI.UI_GraphicComponents.view_overlay_controls import ViewOverlayControls #type: ignore

EVENT_DEBUG = False
CLASS_DEBUG = False
SCENE_DEBUG = False
MOVE_DEBUG = False
WHEEL_DEBUG = False
REMOVE_DEBUG = False
EDGE_CUT_DEBUG = False

MODE_NOOP = 1
MODE_EDGEDRAG = 2
MODE_EDGE_CUT = 3

EDGE_DRAG_START_THRESHOLD = 20

class NodeEditor_QGraphicView(QtWidgets.QGraphicsView):

    scene_mouse_position_changed = Signal(int, int)

    def __init__(self, grScene, parent=None):
        super().__init__(parent)

        self.grScene = grScene

        self.setAcceptDrops(True)

        self.setScene(self.grScene)
        
        self.initViewItems()
        self.initViewStates()
        self.initUI()

    def initViewItems(self):
        self.dragging_edge = NodeEditorDragEdge(self)
        self.cutting_edge = NodeEditorCutLine()
        self.grScene.addItem(self.cutting_edge)

    def initViewStates(self):
        self.mode = MODE_NOOP
        self.is_dragging_rubber_band_rectangle = False

    def initUI(self) -> None:
        #Set Render Attributes
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

        #set scroll Bar Policies
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

        self._drag_enter_listeners = []
        self._drop_listeners = []

        #zoom Properties
        self.zoom_content_visibility_threshold = 9
        self.clamp_zoom = True
        self.zoom_in_factor = 1.25
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = [1, 20]

        self.is_content_visible = False if self.zoom <= self.zoom_content_visibility_threshold else True

        self.last_mouse_position = None

        #on-screen zoom/pan cluster. Tracked with an explicit flag rather than
        #isVisible(), which is False until the whole editor is shown and would
        #make the menu's checkmark lie on startup.
        self.overlay_controls = ViewOverlayControls(self)
        self.overlay_controls_visible = True
        self.overlay_controls.reposition()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay_controls.reposition()

    def setOverlayControlsVisible(self, is_visible):
        self.overlay_controls_visible = is_visible
        self.overlay_controls.setVisible(is_visible)
        if is_visible:
            self.overlay_controls.reposition()

    def areOverlayControlsVisible(self):
        return self.overlay_controls_visible

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
        if event.button() == Qt.MiddleButton:
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
            self.centerView()
        elif event.key() == Qt.Key_Escape:
            self.cancelActiveDragModes()
        elif event.key() == Qt.Key_1:
            self.setDisplayModeForSelectedNodes(NodeEditor_QGraphicNode.DISPLAY_MODE_COLLAPSED)
        elif event.key() == Qt.Key_2:
            self.setDisplayModeForSelectedNodes(NodeEditor_QGraphicNode.DISPLAY_MODE_CONNECTIONS_ONLY)
        elif event.key() == Qt.Key_3:
            self.setDisplayModeForSelectedNodes(NodeEditor_QGraphicNode.DISPLAY_MODE_FULL)
        elif event.key() == Qt.Key_M:
            self.toggleDisabledForSelectedNodes()
        else:
            super().keyPressEvent(event)

    def toggleDisabledForSelectedNodes(self) -> None:
        #generic across both canvases - both rig-component nodes and pipeline
        #steps expose a disabled_checkbox on their properties (different classes,
        #same attribute name/shape). Driven through the checkbox itself, not by
        #setting is_disabled directly, so its stateChanged wiring (which is what
        #actually updates is_disabled and marks things modified on each class)
        #fires normally and the checkbox stays visually in sync if its properties
        #panel is open.
        selected_nodes = self.grScene.scene.getSelectedNodes()
        if not selected_nodes:
            return

        applicable_nodes = [gr_node for gr_node in selected_nodes if hasattr(gr_node.node.properties, 'disabled_checkbox')]
        if not applicable_nodes:
            return

        #if any selected node is currently enabled, this toggle disables all of
        #them; only re-enables when every selected node was already disabled -
        #mirrors how a single keypress across a mixed selection should behave
        new_state = not all(gr_node.node.properties.is_disabled for gr_node in applicable_nodes)

        for gr_node in applicable_nodes:
            gr_node.node.properties.disabled_checkbox.setChecked(new_state)
            gr_node.update()

        self.grScene.scene.history.storeHistory("Toggled Node Disabled State", set_modified = True)

    def cancelActiveDragModes(self) -> None:
        if self.mode == MODE_EDGEDRAG:
            self.dragging_edge.cancelEdgeDrag()
            self.mode = MODE_NOOP
        elif self.mode == MODE_EDGE_CUT:
            self.cutting_edge.line_points = []
            self.cutting_edge.update()
            self.mode = MODE_NOOP

    def setDisplayModeForSelectedNodes(self, mode) -> None:
        selected_nodes = self.grScene.scene.getSelectedNodes()
        if not selected_nodes:
            return

        for gr_node in selected_nodes:
            gr_node.display_mode = mode

        self.grScene.scene.history.storeHistory("Changed Node Display Mode", set_modified = True)
        
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

        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

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
            elif isinstance(item_on_relase_event, QtWidgets.QGraphicsProxyWidget):
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: Item Clicked On:: ", item_on_relase_event)
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: Node has sockets:: ")
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t Amount of Sockets:: ", len(item_on_relase_event.widget().node.inputs + item_on_relase_event.widget().node.outputs))
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t Input Sockets:: " )
                for socket in item_on_relase_event.widget().node.inputs:
                    print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t\t ", socket)
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t Output Sockets:: " )
                for socket in item_on_relase_event.widget().node.outputs:
                    print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t\t ", socket)
            elif isinstance(item_on_relase_event, NodeEditor_QGraphicNode) or isinstance(item_on_relase_event, QtWidgets.QGraphicsTextItem):
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: Item Clicked On:: ", item_on_relase_event)
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: Node has sockets:: ")
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t Amount of Sockets:: ", len(item_on_relase_event.node.inputs + item_on_relase_event.node.outputs))
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t Input Sockets:: " )
                for socket in item_on_relase_event.node.inputs:
                    print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t\t ", socket)
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t Output Sockets:: " )
                for socket in item_on_relase_event.node.outputs:
                    print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t\t ", socket)
            else:
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: Item Clicked On:: ", item_on_relase_event)

        if SCENE_DEBUG and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: Items in Scene:: ")
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: \tNodes:: ")
            for node in self.grScene.scene.nodes:
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t\t", node)
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t", len(self.grScene.scene.nodes)," Node")
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: \tEdges:: ")
            for edge in self.grScene.scene.edges:
                print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t\t", edge)
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t", len(self.grScene.scene.edges), " Edges")
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: Items in GraphicScene:: ")
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: \tGraphicNodes")
            item_counter = 0
            for item in self.grScene.items():
                if  issubclass(type(item), NodeEditor_QGraphicNode) or isinstance(item, NodeEditor_QGraphicNode):
                    print("GRAPHICSVIEW:: --middleMouseButtonPress:: Graphic Node:: \t", item)
                    item_counter += 1
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t", item_counter, " GraphicNodes")
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: \tGraphicEdges")
            item_counter = 0
            for item in self.grScene.items():
                if isinstance(item, NodeEditor_QGraphicEdge):
                    print("GRAPHICSVIEW:: --middleMouseButtonPress:: Graphic Edge:: \t", item)
                    item_counter += 1
            print("GRAPHICSVIEW:: --middleMouseButtonPress:: \t", item_counter, " GraphicEdges")
            
    def isNodeRelatedItem(self, item) -> bool:
        #anything visually part of a node - not just the grNode/title item itself,
        #which are the only things carrying a direct .node attribute, but also the
        #proxy widget hosting its socket labels and the socket dots themselves.
        #Without this, shift/ctrl-click additive selection only worked when the
        #click happened to land on the title bar.
        if item is None:
            return True
        if isinstance(item, NodeEditor_QGraphicEdge):
            return True
        if hasattr(item, 'node'):
            return True
        if isinstance(item, (NodeEditor_QGraphicSocket, NodeEditor_QGraphicCollapsedSocket)):
            return True
        if isinstance(item, QtWidgets.QGraphicsProxyWidget):
            return True
        return False

    def leftMouseButtonPress(self, event):

        item_on_click = self.getItemAtEvent(event)
        self.last_mouse_button_press_position = self.mapToScene(event.pos())

        if self.isNodeRelatedItem(item_on_click):

            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                if EVENT_DEBUG: print("GRAPHICSVIEW:: --leftMouseButtonPress:: Shift Click On Node")

                event.ignore()
                fake_mouse_event = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers() | Qt.KeyboardModifier.ControlModifier)
                super().mousePressEvent(fake_mouse_event)
                return

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

        if EVENT_DEBUG: print("GRAPHICSVIEW:: --leftMouseButtonPress:: Item:: ", item_on_click)

        if item_on_click is None:
            
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.mode = MODE_EDGE_CUT
                if EDGE_CUT_DEBUG: print("GRAPHICSVIEW:: --leftMouseButtonPress:: Setting Edge Cut Mode ", self.mode)

                fake_mouse_event = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(), Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fake_mouse_event)
                return
            
            else:
                if EVENT_DEBUG: print("NODEEDITORVIEW:: --leftMouseButtonRelease:: Rubber Band Dragging On")
                self.is_dragging_rubber_band_rectangle = True

        super().mousePressEvent(event)

    def rightMouseButtonPress(self, event):
        return super().mousePressEvent(event)
    
    def leftMouseButtonRelease(self, event):

        item_on_release = self.getItemAtEvent(event)

        if self.isNodeRelatedItem(item_on_release):

            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                if EVENT_DEBUG:
                    print("GRAPHICSVIEW:: --leftMouseButtonRelease:: Shift Release On Node")
                    print("GRAPHICSVIEW:: --leftMouseButtonRelease:: Adding ", item_on_release, " to selection")
                event.ignore()
                fake_mouse_event = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(), Qt.LeftButton, Qt.NoButton, event.modifiers() | Qt.KeyboardModifier.ControlModifier)
                super().mouseReleaseEvent(fake_mouse_event)
                return

        if self.getDistanceFromLastLeftMousePressEvent(event) > math.pow(EDGE_DRAG_START_THRESHOLD, 2):
            if self.mode == MODE_EDGEDRAG:
                self.mode = MODE_NOOP
                drag_result = self.dragging_edge.endEdgeDrag(item_on_release)
                if drag_result: return

        if EVENT_DEBUG: 
            print("GRAPHICSVIEW:: --leftMouseButtonRelease:: Mode:: ", self.mode)
            print("GRAPHICSVIEW:: --leftMouseButtonRelease:: Item:: ", item_on_release)
        
        if self.mode == MODE_EDGE_CUT:
            if EDGE_CUT_DEBUG: print("GRAPHICSVIEW:: --leftMouseButtonRelease:: Cutting Intersecting Edges")
            self.cutIntersectingEdges()

            if EDGE_CUT_DEBUG: print("GRAPHICSVIEW:: --leftMouseButtonRelease:: Resetting Cut Line Points")
            self.cutting_edge.line_points = []

            if EDGE_CUT_DEBUG: print("GRAPHICSVIEW:: --leftMouseButtonRelease:: update Cutline")
            self.cutting_edge.update()

            if EDGE_CUT_DEBUG: print("GRAPHICSVIEW:: --leftMouseButtonRelease:: Reset Mode")
            self.mode = MODE_NOOP
            return

        if self.is_dragging_rubber_band_rectangle:
            if EVENT_DEBUG: print("NODEEDITORVIEW:: --leftMouseButtonRelease:: Rubber Band Dragging Off")
            self.is_dragging_rubber_band_rectangle = False

            current_selected_items = self.grScene.selectedItems()
            if EVENT_DEBUG: print("GRAPHICSVIEW:: --leftMouseButtonRelease:: Last Stored Selection:: ", self.grScene.scene._last_selected_items)
            if EVENT_DEBUG: print("GRAPHICSVIEW:: --leftMouseButtonRelease:: Currently Selected Items:: ", current_selected_items)
            if current_selected_items != self.grScene.scene._last_selected_items:
                if current_selected_items == []:
                    self.grScene.itemsDeselected.emit()
                else:
                    self.grScene.itemSelected.emit()
                if EVENT_DEBUG: print("GRAPHICSVIEW:: --leftMouseButtonRelease:: Setting Scene Last Selected Items from:: ", self.grScene.scene._last_selected_items, " to:: ", current_selected_items)
                self.grScene.scene._last_selected_items = current_selected_items
            return 
        
        if item_on_release is None:
            self.grScene.itemsDeselected.emit()

        return super().mouseReleaseEvent(event)
    
    def rightMouseButtonRelease(self, event):
        return super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):

        scene_event_mouse_position = self.mapToScene(event.pos())

        if MOVE_DEBUG: print("GRAPHICSVIEW:: --mouseMoveEvent:: ", self.mode)
        if MOVE_DEBUG: print("GRAPHICSVIEW:: --mouseMoveEvent:: is EdgeDrag:: ", self.mode == MODE_EDGEDRAG)
        if MOVE_DEBUG: print("GRAPHICSVIEW:: --mouseMoveEvent:: MODE_EDGE_DRAG ", MODE_EDGEDRAG)

        if self.mode == MODE_EDGEDRAG:
            self.dragging_edge.updateDestination(scene_event_mouse_position.x(), scene_event_mouse_position.y())
        
        if self.mode == MODE_EDGE_CUT:
            self.cutting_edge.line_points.append(scene_event_mouse_position)
            self.cutting_edge.update()

        self.last_mouse_position = scene_event_mouse_position

        self.scene_mouse_position_changed.emit(int(scene_event_mouse_position.x()), int(scene_event_mouse_position.y()))
        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        if WHEEL_DEBUG : print("GRAPHICSVIEW:: --wheelEvent:: Starting WheelEvent")
        self.applyZoomStep(zoom_in = event.angleDelta().y() > 0)

    def zoomIn(self):
        self.applyZoomStep(zoom_in = True, anchor_to_center = True)

    def zoomOut(self):
        self.applyZoomStep(zoom_in = False, anchor_to_center = True)

    def panBy(self, horizontal_amount, vertical_amount):
        """Shift the view by a number of pixels. Used by the on-screen controls -
        dragging with the middle mouse button goes through Qt's own ScrollHandDrag
        instead, so both end up moving the same scrollbars."""
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + horizontal_amount)
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() + vertical_amount)

    def applyZoomStep(self, zoom_in = True, anchor_to_center = False):
        #shared by the wheel and the on-screen zoom buttons, so both keep
        #self.zoom, the clamping and the content-visibility threshold in step
        zoomOutFactor = 1 / self.zoom_in_factor

        if zoom_in:
            zoomFactor = self.zoom_in_factor
            self.zoom += self.zoom_step
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoom_step

        clamped = False
        if self.zoom < self.zoom_range[0]:  self.zoom, clamped = self.zoom_range[0], True
        if self.zoom > self.zoom_range[1]:  self.zoom, clamped = self.zoom_range[1], True

        if not clamped or self.clamp_zoom is False:
            if anchor_to_center:
                #the view anchors zoom under the cursor, which for a button press
                #is the button itself - zoom around the middle of the view instead
                previous_anchor = self.transformationAnchor()
                self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
                self.scale(zoomFactor, zoomFactor)
                self.setTransformationAnchor(previous_anchor)
            else:
                self.scale(zoomFactor, zoomFactor)

        #Set Visibility of the nodes content depending on the zoom Level.
        #Node types that draw no per-socket labels have no content widget at all
        #(Node_Content_Class = None, e.g. pipeline steps) - calling show() on those
        #used to raise AttributeError, and before they opted out it floated their
        #parentless content widget as a stray top-level window
        if self.zoom <= self.zoom_content_visibility_threshold:
            if self.is_content_visible:
                for node in self.grScene.scene.nodes:
                    if node.content is not None:
                        node.content.hide()
            self.is_content_visible = False
        else:
            if not self.is_content_visible:
                for node in self.grScene.scene.nodes:
                    if node.content is not None:
                        node.content.show()
            self.is_content_visible = True
    
    def dragEnterEvent(self, event):
        for callback in self._drag_enter_listeners: callback(event)

    def dropEvent(self, event):
        for callback in self._drop_listeners: callback(event)

    def connectViewDragEnterListenerCallback(self, callback):
        self._drag_enter_listeners.append(callback)
    
    def connectViewDropListenerCallback(self, callback):
        self._drop_listeners.append(callback)

    def cutIntersectingEdges(self):
        for index in range(len(self.cutting_edge.line_points ) -1):

            point1 = self.cutting_edge.line_points[index]
            point2 = self.cutting_edge.line_points[index + 1]

            for edge in self.grScene.scene.edges:
                if edge.grEdge.intersectsWith(point1, point2):
                    edge.remove()

        self.grScene.scene.history.storeHistory("Delete Cutted Edges", set_modified = True)

    def displayErrorMessage(self, message):
        parent_widget = self.parentWidget().parentWidget().parentWidget().parentWidget().parentWidget().parentWidget()
        print("parent Widget:: ", parent_widget.__class__)
        print(dir(parent_widget))
        parent_widget.statusBar().showMessage(message, 5000)
        parent_widget.set_statusBar_color("#FFc43721", 5000)
        
    def deleteSelected(self):
        selected_items = self.grScene.selectedItems()
        selected_nodes = []
        selected_edges = []

        for item in selected_items:
            if isinstance(item, NodeEditor_QGraphicEdge):
                selected_edges.append(item)
            elif hasattr(item, 'node'):
                selected_nodes.append(item)

        if REMOVE_DEBUG: 
            print("GRAPHICSVIEW:: --deleteSelected:: Selected Items to be Removed: ")
            for item in selected_items:
                print("GRAPHICSVIEW:: --deleteSelected:: Graphical Item:: \t", item)
            print("GRAPHICSVIEW:: --deleteSelected:: Selected Nodes to be Removed:: ")
            for node in selected_nodes:
                print("GRAPHICSVIEW:: --deleteSelected:: \tGraphical Node \t", node)
                print("GRAPHICSVIEW:: --deleteSelected:: \tLogical Node \t", node.node)
            print("GRAPHICSVIEW:: --deleteSelected:: Selected Edges to be Removed:: ")
            for edge in selected_edges:
                print("GRAPHICSVIEW:: --deleteSelected:: \tGraphical Edge\t", edge)
                print("GRAPHICSVIEW:: --deleteSelected:: \tLogical Edge \t", edge.edge)

        for node in selected_nodes:
            if not getattr(node.node, 'is_deletable', True):
                if REMOVE_DEBUG: print("GRAPHICSVIEW:: --deleteSelected:: skipping non-deletable node:: ", node.node)
                continue
            if node.node in node.node.scene.nodes:
                if REMOVE_DEBUG: print("GRAPHICSVIEW:: --deleteSelected:: about to Remove Node")
                node.node.remove()

        for edge in selected_edges:
            if edge.edge in edge.edge.scene.edges:
                edge.edge.remove()

        self.grScene.scene.history.storeHistory("Deleted Selected", set_modified = True)

    def centerView(self):
        selected_items = self.grScene.selectedItems()
        
        if len(selected_items) == 0:
            if self.grScene.scene.nodes == []:
                self.centerOn(0, 0)
            else:
                combined_bounding_rectangle = QRectF()
                for node in self.grScene.scene.nodes:
                    combined_bounding_rectangle = combined_bounding_rectangle.united(node.grNode.mapToScene(node.grNode.boundingRect()).boundingRect())
                self.centerOn(combined_bounding_rectangle.center())

        elif len(selected_items) > 1:
            combined_bounding_rectangle = QRectF()

            for item in selected_items:
                if hasattr(item, "node"):
                    combined_bounding_rectangle = combined_bounding_rectangle.united(item.mapToScene(item.boundingRect()).boundingRect())

            self.centerOn(combined_bounding_rectangle.center())
        else:
            if CLASS_DEBUG: print("node:: ", selected_items[0])
            if CLASS_DEBUG: print("nodeWidth:: ", selected_items[0].width)
            if CLASS_DEBUG: print("nodeHeight:: ", selected_items[0].height)
            view_position = QPointF(selected_items[0].pos().x() + (selected_items[0].width / 2), selected_items[0].pos().y() + (selected_items[0].height / 2))
            self.centerOn(view_position)

    def getItemAtEvent(self, event):
        return self.itemAt(event.pos())
    
    def getDistanceFromLastLeftMousePressEvent(self, event):
        current_event_scene_position = self.mapToScene(event.pos())
        distance_to_last_left_mouse_press = current_event_scene_position - self.last_mouse_button_press_position

        return math.pow(distance_to_last_left_mouse_press.x(), 2) + math.pow(distance_to_last_left_mouse_press.y(), 2)
    
    def drawForeground(self, painter, rect):

        rubber_band_rect = self.rubberBandRect()

        if not rubber_band_rect.isNull():
            # Set custom pen and brush for the rubber band appearance
            painter.setPen(QPen(QColor(0, 0, 0, 0)))
            painter.setBrush(QColor(150, 150, 150, 80))  # Translucent fill color

            # Convert rubber band rectangle to scene coordinates and draw
            scene_rect = self.mapToScene(rubber_band_rect).boundingRect()
            painter.drawRect(scene_rect)
        
        super().drawForeground(painter, rect)