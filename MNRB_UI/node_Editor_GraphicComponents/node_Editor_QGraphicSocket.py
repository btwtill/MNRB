from PySide2 import QtWidgets # type: ignore
from PySide2.QtGui import QColor, QPen, QBrush # type: ignore
from PySide2.QtCore import QRectF, Qt #type: ignore

SOCKET_COLOR = [
    QColor("#FFFF7700"),
    QColor("#FF528220"),
    QColor("#FF0056a6"),
    QColor("#FFa86db1"),
    QColor("#FFb54747"),
    QColor("#FFdbe220")
]

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
        
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        if not self.socket.accept_multi_edges:
            painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)
        else:
            painter.drawRect(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

        if self.is_drawing_bounding_box:
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.boundingRect())

    def __str__(self): return "ClassInstance::%s::  %s..%s" % (__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])