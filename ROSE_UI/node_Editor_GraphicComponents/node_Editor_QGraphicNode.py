from PySide6 import QtWidgets # type:ignore
from PySide6.QtCore import Qt, QRectF, QPointF # type: ignore
from PySide6.QtGui import QFont, QFontMetrics, QBrush, QPen, QColor, QPainterPath # type: ignore
from MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicSocket import NodeEditor_QGraphicCollapsedSocket #type: ignore

SELECTION_DEBUG = False
EVENT_DEBUG = False
CLASS_DEBUG = False

class NodeEditor_QGraphicNode(QtWidgets.QGraphicsItem):

    #node display modes, matching Maya's own Node Editor 1/2/3 convention
    DISPLAY_MODE_COLLAPSED = 1
    DISPLAY_MODE_CONNECTIONS_ONLY = 2
    DISPLAY_MODE_FULL = 3

    def __init__(self, node, parent = None):
        super().__init__(parent)

        self.node = node

        self._was_moved = False
        self._last_selected_state = False

        self._raw_title = ""
        self._display_mode = self.DISPLAY_MODE_FULL

        self.initGraphicElements()
        self.initContent()
        self.initUI()
        self.wrapGrNodeToSockets()

    @property
    def title(self): return self._title

    @title.setter
    def title(self, value):
        self._raw_title = value
        available_width = max(self.width - 2 * self._title_padding, 0)
        self._title = QFontMetrics(self._title_font).elidedText(value, Qt.ElideRight, int(available_width))
        self.title_item.setPlainText(self._title)

    @property
    def content(self): return self.node.content if self.node else None

    @property
    def display_mode(self): return self._display_mode

    @display_mode.setter
    def display_mode(self, value):
        self._display_mode = value
        self.wrapGrNodeToSockets()

    @property
    def width(self): return self._width

    @width.setter
    def width(self, value):
            self._width = value

    @property
    def height(self): return self._height

    @height.setter
    def height(self, value):
        if value >= 60:
            self._height = value
        else:
            self._height = 60

    def initGraphicElements(self):
        #initialize Graphic element variables
        self.width = 100
        self.height = 60

        self.socket_padding = 12.0
        self.socket_radius = 5.0

        self._edge_roundness = 5
        self._edge_padding = 5

        self.title_height = 20
        self.collapsed_width = 80

        #initialize the variables for the Graphical Elements
        self._title_font = QFont("Verdana", 8)
        self._title_padding = 10

        self._default_color = QColor("#7F000000")
        self._selected_color = QColor("#FFFFA637")
        self._title_color = Qt.white
        self._title_backgroundColor = QColor("#FF181818")
        self._content_color = QColor("#EF1F1F1F")
        self._valid_color = QColor("#FF336600")
        self._invalid_color = QColor("#FFc43721")

        self._default_pen = QPen(self._default_color)
        self._selected_pen = QPen(self._selected_color)
        self._valid_pen = QPen(self._valid_color)
        self._valid_pen.setJoinStyle(Qt.MiterJoin)
        self._valid_pen.setMiterLimit(5)
        self._invalid_pen = QPen(self._invalid_color)
        self._invalid_pen.setJoinStyle(Qt.MiterJoin)
        self._invalid_pen.setMiterLimit(5)

        self._title_background_brush = QBrush(self._title_backgroundColor)
        self._content_brush = QBrush(self._content_color)
        self._valid_brush = QBrush(self._valid_color)
        self._invalid_brush = QBrush(self._invalid_color)

        #initialize the node title
        self.title_item = QtWidgets.QGraphicsTextItem(self)
        self.title_item.node = self.node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._title_padding, 0)
        #QTextDocument adds its own 4px margin on every side by default, on top of
        #_title_padding - left in place, elidedText's fit calculation runs out of room
        #and the title wraps even though it was just sized to fit exactly.
        self.title_item.document().setDocumentMargin(0)
        self.title_item.setTextWidth(
            self.width  - 2 * self._title_padding
        )
        self.title = self.node.title

        #merge-point dots for collapsed (display mode 1) nodes - all incoming
        #connections funnel to one, all outgoing to the other. Only shown while
        #collapsed; positioned/toggled in wrapGrNodeToSockets().
        self.merged_input_socket = NodeEditor_QGraphicCollapsedSocket(self)
        self.merged_output_socket = NodeEditor_QGraphicCollapsedSocket(self)
        self.merged_input_socket.setVisible(False)
        self.merged_output_socket.setVisible(False)

    def initContent(self):
        if self.content is not None:
            self.content.setGeometry(self._edge_padding, self.title_height + self._edge_padding, self.width - 2 * self._edge_padding, self.height - 2 *  self._edge_padding - self.title_height )

        self.grContent = self.node.scene.grScene.addWidget(self.content)
        self.grContent.setParentItem(self)

    def initUI(self):
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)

        self.is_drawing_bounding_box = False
    
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        if event.buttons() & Qt.LeftButton:
            if EVENT_DEBUG: 
                print("GRAPHICSNODE:: -mouseMoveEvent:: Start")
                print("GRAPHICSNODE:: -mouseMoveEvent:: Left Button Mouse Moved")
                print("GRAPHICSNODE:: -mouseMoveEvent:: Nodes to be updated:: ")
                for node in self.node.scene.nodes:
                    print("GRAPHICSNODE:: -mouseMoveEvent:: Node: ", node)
                    print("GRAPHICSNODE:: -mouseMoveEvent:: \t with GrNode:: ", node.grNode)

            for node in self.node.scene.nodes:
                if node.grNode.isSelected():
                    node.updateConnectedEdges()

            self._was_moved = True

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.storeHistory("Node Moved", set_modified = True)

            self.node.scene.reset_last_selected_states()
            self.doSelect()
            self.node.scene._last_selected_items = self.node.scene.getSelectedItems()

        if SELECTION_DEBUG: print("GRAPHICNODE:: --mouseReleaseEvent:: Last Scene Selection:: ", self.node.scene._last_selected_items)
        if SELECTION_DEBUG: print("GRAPHICNODE:: --mouseReleaseEvent:: Current Selected Items:: ", self.node.scene.getSelectedItems())

        if self._last_selected_state != self.isSelected() or self.node.scene._last_selected_items != self.node.scene.getSelectedItems():
            self.node.scene.reset_last_selected_states()
            self._last_selected_state = self.isSelected()
            self.onSelected()
            if SELECTION_DEBUG: print("GRAPHICNODE:: --mouseReleaseEvent:: Last Scene Selection after --onSelected()", self.node.scene._last_selected_items)
            if SELECTION_DEBUG: print("GRAPHICNODE:: --mouseReleaseEvent:: Items Selected In Scene after --onSelected():: ", self.node.scene.getSelectedItems())
            
    def setIsDrawingBoundingBox(self, value=True):
        self.is_drawing_bounding_box = value

    def wrapGrNodeToSockets(self):
        if CLASS_DEBUG: print("%s::wrapGRNodeToSockets:: " % self.__class__.__name__)

        all_sockets = self.node.inputs + self.node.outputs
        #the very first call happens before initSockets() has run, while inputs/outputs
        #are still the raw constructor arguments rather than real Socket objects
        sockets_exist = bool(all_sockets) and hasattr(all_sockets[0], 'hasEdge')
        labels = self.content.getContentLabels() if self.content is not None else []
        pairs = list(zip(all_sockets, labels)) if sockets_exist else []

        if self.display_mode == self.DISPLAY_MODE_COLLAPSED:
            visible_pairs = []
            #bypass the height property's 60px floor - a collapsed node is meant
            #to be smaller than that, just the title row
            self._height = self.title_height + self.socket_padding
            self.width = self.collapsed_width
        else:
            if self.display_mode == self.DISPLAY_MODE_CONNECTIONS_ONLY and sockets_exist:
                visible_pairs = [pair for pair in pairs if pair[0].hasEdge()]
            else:
                visible_pairs = pairs

            full_socket_height = self.socket_padding + self.socket_radius
            socket_count_for_height = len(visible_pairs) if sockets_exist else len(all_sockets)
            self.height = (socket_count_for_height * full_socket_height) + self.title_height + self.socket_padding
            self.width = self.computeRequiredWidth(visible_pairs if sockets_exist else None)

        if CLASS_DEBUG: print("%s::wrapGRNodeToSockets:: new grNode Height/Width" % self.__class__.__name__, self.height, self.width)

        #show/hide each real socket dot + label to match the current display mode
        visible_sockets = set(socket for socket, _ in visible_pairs)
        for socket, label in pairs:
            is_visible = socket in visible_sockets
            label.setVisible(is_visible)
            socket.grSocket.setVisible(is_visible)

        #re-apply the title width/elision and the content widget geometry, both of which
        #depend on self.width and would otherwise only ever be set once at construction time
        self.title_item.setTextWidth(self.width - 2 * self._title_padding)
        self.title = self._raw_title

        if self.content is not None:
            content_rect = QRectF(self._edge_padding, self.title_height + self._edge_padding, self.width - 2 * self._edge_padding, self.height - 2 * self._edge_padding - self.title_height)
            self.content.setGeometry(content_rect.toRect())
            #QGraphicsProxyWidget can re-fit itself to the embedded widget's layout
            #sizeHint via a queued LayoutRequest after addSocketLabel/removeLastLabel,
            #undoing the line above. Set the proxy item's own geometry too so the
            #actually-drawn item stays authoritative regardless of that timing.
            if self.grContent is not None:
                self.grContent.setGeometry(content_rect)

        #socket dots are positioned once, at socket-creation time, against whatever
        #grNode.width/height was at that moment. Now that width/height can change later
        #(e.g. more sockets added, or the display mode changes), every existing socket
        #needs to be re-placed against the new size, or older sockets are left stranded.
        if sockets_exist:
            for socket in all_sockets:
                socket.setPosition()
            self.node.updateConnectedEdges()

        #the two merge-point dots only ever show in collapsed mode
        is_collapsed = self.display_mode == self.DISPLAY_MODE_COLLAPSED
        self.merged_input_socket.setVisible(is_collapsed)
        self.merged_output_socket.setVisible(is_collapsed)
        if is_collapsed:
            self.merged_input_socket.setPos(*self.getMergedSocketPosition(1))   # 1 == LEFT (inputs)
            self.merged_output_socket.setPos(*self.getMergedSocketPosition(2))  # 2 == RIGHT (outputs)

    def getMergedSocketPosition(self, position):
        x = 0 if position == 1 else self.width  # 1 == LEFT (inputs), 2 == RIGHT (outputs)
        y = self.title_height / 2
        return [x, y]

    def computeRequiredWidth(self, visible_pairs = None):
        #width is driven only by socket labels, not by the title - the title is elided
        #to fit instead of growing the node, so renaming a node doesn't resize it.
        minimum_width = 100
        required_width = minimum_width

        if visible_pairs is not None:
            labels = [label for _, label in visible_pairs]
        elif self.content is not None:
            labels = self.content.getContentLabels()
        else:
            labels = []

        for socket_label in labels:
            label_width = socket_label.fontMetrics().horizontalAdvance(socket_label.text())
            required_width = max(required_width, label_width + 2 * self._edge_padding + 2 * self.socket_padding)

        return max(required_width, minimum_width)

    def onSelected(self):
        if SELECTION_DEBUG: print("GRAPHICNODE:: --onSelected:: ")
        self.node.scene.grScene.itemSelected.emit()

    def doSelect(self, new_selection_state = True):
        self.setSelected(new_selection_state)
        self._last_selected_state = new_selection_state
        if new_selection_state: self.onSelected()

    def boundingRect(self):
        return QRectF(
            0, 
            0, 
            self.width,
            self.height,
            ).normalized()

    # Paint method to draw the square
    def paint(self, painter, option, widget=None):

        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0,0, self.width, self.title_height, self._edge_roundness, self._edge_roundness)
        path_title.addRect(0, self.title_height -self._edge_roundness, self._edge_roundness, self._edge_roundness)
        path_title.addRect(self.width - self._edge_roundness, self.title_height -self._edge_roundness, self._edge_roundness, self._edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._title_background_brush)
        painter.drawPath(path_title.simplified())

        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self._edge_roundness, self._edge_roundness)
        path_content.addRect(0, self.title_height, self._edge_roundness, self._edge_roundness)
        path_content.addRect(self.width - self._edge_roundness, self.title_height, self._edge_roundness, self._edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._content_brush)
        painter.drawPath(path_content.simplified())

        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self._edge_roundness, self._edge_roundness)
        painter.setPen(self._default_pen if not self.isSelected() else self._selected_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())

        path_valid_icon = QPainterPath()
        path_valid_icon.setFillRule(Qt.WindingFill)
        top_left = QPointF(self.width - self.title_height + 4.0, 0 + 1.0)
        top_right = QPointF(self.width - 1.0, 0 + 1.0)
        lower_left = QPointF(self.width - self.title_height - 1.0, self.title_height - 1.0)
        lower_right = QPointF(self.width - 1.0, self.title_height - 6.0)
        top_right_rounded_upper = QPointF(self.width - self._edge_roundness - 1.0 , 0 + 1.0)
        top_right_rounded_lower = QPointF(self.width - 1.0, 0 + 1.0 + self._edge_roundness)

        path_valid_icon.moveTo(top_left)
        path_valid_icon.lineTo(top_right_rounded_upper)
        path_valid_icon.quadTo(top_right, top_right_rounded_lower)
        path_valid_icon.lineTo(lower_right)
        path_valid_icon.lineTo(lower_left)
        path_valid_icon.lineTo(top_left)

        subtraction_path = QPainterPath()
        subtraction_path.moveTo(top_left)
        subtraction_path.lineTo(lower_right)
        subtraction_path.lineTo(lower_left)
        subtraction_path.lineTo(top_left)

        validation_icon_path = path_valid_icon.subtracted(subtraction_path)

        painter.setPen(self._valid_pen if self.node.properties.is_valid else self._invalid_pen)
        painter.setBrush(self._valid_brush if self.node.properties.is_valid else self._invalid_brush)
        painter.drawPath(validation_icon_path.simplified())

        #paintBounding Rect
        if self.is_drawing_bounding_box:
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.drawRect(self.boundingRect())
            
    def __str__(self): return "ClassInstance::%s::  %s..%s" % (__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])