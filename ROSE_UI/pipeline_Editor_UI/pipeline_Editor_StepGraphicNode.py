from PySide6 import QtWidgets #type: ignore
from PySide6.QtCore import Qt, QRectF #type: ignore
from PySide6.QtGui import QFont, QFontMetrics, QBrush, QPen, QColor, QPainterPath, QTextOption #type: ignore

class PipelineStep_QGraphicNode(QtWidgets.QGraphicsItem):
    """Deliberately simple graphics node for pipeline steps - just a title and one
    big input/output dot each, no per-socket labels or dynamic sizing. This is a
    fresh implementation rather than a NodeEditor_QGraphicNode subclass, since the
    rig-component node's whole layout model (title + a content area of per-socket
    label rows, dynamically resized) doesn't apply here - every step has exactly
    one in, one out, and a fixed size."""

    def __init__(self, node, parent = None):
        super().__init__(parent)

        self.node = node

        self._was_moved = False
        self._last_selected_state = False
        self._raw_title = ""

        #fixed size - no dynamic content to size around. Compact rather than a
        #long bar: the title wraps onto two lines instead of stretching the card
        self.width = 124
        self.height = 64
        self.title_height = self.height

        #bigger than the rig-node default (5.0) - "one big in and one big output"
        self.socket_radius = 8.0
        self.socket_padding = 12.0
        #round, not the rig graph's squared multi-edge socket
        self.multi_socket_roundness = self.socket_radius

        self._edge_roundness = 14
        self._title_font = QFont("Verdana", 8, QFont.Bold)
        self._title_padding = 14
        self._max_title_lines = 2

        self._default_color = QColor("#7F000000")
        self._selected_color = QColor("#FFFFA637")
        self._title_color = Qt.white
        self._background_color = QColor("#FF34363A")
        #a thin band along the top, in the socket green, so a step reads as a
        #pipeline step at any zoom
        self._accent_color = QColor("#FF5FBF6A")
        self._accent_height = 4
        self._disabled_line_color = QColor("#FFCC4444")

        self._default_pen = QPen(self._default_color)
        self._selected_pen = QPen(self._selected_color)
        self._selected_pen.setWidthF(2.0)
        self._background_brush = QBrush(self._background_color)

        #no content widget at all - pipeline steps have no per-socket labels to show
        self.content = None
        self.grContent = None

        self.title_item = QtWidgets.QGraphicsTextItem(self)
        self.title_item.node = self.node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.document().setDocumentMargin(0)
        self.title_item.setTextWidth(self.width - 2 * self._title_padding)
        title_option = QTextOption(Qt.AlignHCenter)
        title_option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.title_item.document().setDefaultTextOption(title_option)
        self.title = self.node.title

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)

        self.is_drawing_bounding_box = False

    @property
    def title(self): return self._title

    @title.setter
    def title(self, value):
        self._raw_title = value
        available_width = max(self.width - 2 * self._title_padding, 0)
        #wraps over up to _max_title_lines, eliding only what still does not fit
        self._title = QFontMetrics(self._title_font).elidedText(
            value, Qt.ElideRight, int(available_width * self._max_title_lines))
        self.title_item.setPlainText(self._title)

        #centred in the card, below the accent band
        text_height = self.title_item.boundingRect().height()
        free_height = self.height - self._accent_height
        self.title_item.setPos(self._title_padding,
                               self._accent_height + max((free_height - text_height) / 2, 0))

    def wrapGrNodeToSockets(self):
        #fixed size regardless of socket count - every step has exactly one input
        #and one output. Sockets are positioned by PipelineStepNode.getSocketPosition,
        #not by anything here.
        existing_sockets = self.node.inputs + self.node.outputs
        if existing_sockets and hasattr(existing_sockets[0], 'setPosition'):
            for socket in existing_sockets:
                socket.setPosition()
            self.node.updateConnectedEdges()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if event.buttons() & Qt.LeftButton:
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

        if self._last_selected_state != self.isSelected() or self.node.scene._last_selected_items != self.node.scene.getSelectedItems():
            self.node.scene.reset_last_selected_states()
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def setIsDrawingBoundingBox(self, value=True):
        self.is_drawing_bounding_box = value

    def onSelected(self):
        self.node.scene.grScene.itemSelected.emit()

    def doSelect(self, new_selection_state = True):
        self.setSelected(new_selection_state)
        self._last_selected_state = new_selection_state
        if new_selection_state: self.onSelected()

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height).normalized()

    def paint(self, painter, option, widget=None):
        is_disabled = self.node.properties.is_disabled

        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self._edge_roundness, self._edge_roundness)

        #disabled reads as "more transparent", applied only to the fill/outline -
        #the strikethrough line below stays fully opaque so it's always legible
        painter.setOpacity(0.4 if is_disabled else 1.0)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self._background_brush)
        painter.drawPath(path_outline)

        painter.save()
        painter.setClipPath(path_outline)
        painter.setBrush(QBrush(self._accent_color))
        painter.drawRect(QRectF(0, 0, self.width, self._accent_height))
        painter.restore()

        painter.setPen(self._default_pen if not self.isSelected() else self._selected_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline)

        painter.setOpacity(1.0)

        if is_disabled:
            disabled_pen = QPen(self._disabled_line_color)
            disabled_pen.setWidthF(2.5)
            painter.setPen(disabled_pen)
            painter.drawLine(8, self.height - 8, self.width - 8, 8)

        if self.is_drawing_bounding_box:
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.drawRect(self.boundingRect())

    def __str__(self): return "ClassInstance::%s::  %s..%s" % (self.__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])
