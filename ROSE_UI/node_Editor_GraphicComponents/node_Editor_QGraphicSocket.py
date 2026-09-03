from PySide6 import QtWidgets # type: ignore
from PySide6.QtGui import QColor, QPen, QBrush, QPainterPath # type: ignore
from PySide6.QtCore import QRectF, Qt #type: ignore

SOCKET_COLOR = [
    QColor("#FFFF7700"),
    QColor("#FF528220"),
    QColor("#FF0056a6"),
    QColor("#FFa86db1"),
    QColor("#FFb54747"),
    QColor("#FFdbe220")
]

#used only by NodeEditor_QGraphicCollapsedSocket - a display-only merge point for a
#collapsed node's connections, not a real typed SocketTypes entry
COLLAPSED_SOCKET_COLOR = QColor("#FFB0B0B0")

class NodeEditor_QGraphicSocket(QtWidgets.QGraphicsItem):
    def __init__(self, socket):
        super().__init__(socket.node.grNode)

        self.socket = socket

        self.initGraphicElements()
        self.initUI()
    
    def initGraphicElements(self):
        self.radius = self.socket.node.grNode.socket_radius
        self._outline_width = 1.0

        self._background_color = SOCKET_COLOR[self.socket.socket_type]
        self._outline_color = QColor("#FF000000")

        self._pen = QPen(self._outline_color)
        self._pen.setWidthF(self._outline_width)
        self._brush = QBrush(self._background_color)

    def initUI(self):
        self.is_drawing_bounding_box = False

    def setSize(self, size):
        self.radius = size

    def boundingRect(self):
        return QRectF(
            -self.radius - self._outline_width, 
            -self.radius - self._outline_width, 
            2 * (self.radius + self._outline_width),
            2 * (self.radius + self._outline_width),
            ).normalized()

    def paint(self, painter, option, widget=None):
        
        multi_edge_shape = QPainterPath()
        multi_edge_shape.setFillRule(Qt.WindingFill)
        multi_edge_shape.addRoundedRect(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius, 2, 2)

        painter.setPen(self._pen)
        painter.setBrush(self._brush)

        if not self.socket.accept_multi_edges:
            painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)
        else:
            painter.drawPath(multi_edge_shape.simplified())

        if self.is_drawing_bounding_box:
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.boundingRect())

    def __str__(self): return "ClassInstance::%s::  %s..%s" % (__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])


class NodeEditor_QGraphicCollapsedSocket(QtWidgets.QGraphicsItem):
    """Non-interactive merge point drawn on a collapsed (display mode 1) node -
    represents every incoming or every outgoing connection funneled into one dot.
    Deliberately not selectable/draggable: starting a new connection requires
    switching the node back to full display first."""

    def __init__(self, grNode):
        super().__init__(grNode)

        self.grNode = grNode

        self.radius = grNode.socket_radius
        self._outline_width = 1.0

        self._pen = QPen(QColor("#FF000000"))
        self._pen.setWidthF(self._outline_width)
        self._brush = QBrush(COLLAPSED_SOCKET_COLOR)

    def boundingRect(self):
        return QRectF(
            -self.radius - self._outline_width,
            -self.radius - self._outline_width,
            2 * (self.radius + self._outline_width),
            2 * (self.radius + self._outline_width),
            ).normalized()

    def paint(self, painter, option, widget=None):
        multi_edge_shape = QPainterPath()
        multi_edge_shape.setFillRule(Qt.WindingFill)
        multi_edge_shape.addRoundedRect(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius, 2, 2)

        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawPath(multi_edge_shape.simplified())

    def __str__(self): return "ClassInstance::%s::  %s..%s" % (__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])