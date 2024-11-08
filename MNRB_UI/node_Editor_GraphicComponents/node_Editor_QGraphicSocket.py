from PySide2 import QtWidgets # type: ignore
from PySide2.Gui import QColor, QPen, QBrush # type: ignore
from PySide2.QtCore import QRectF, Qt #type: ignore


class NodeEditor_QGraphicSocket(QtWidgets.QGraphicsItem):
    def __init__(self, socket, parent=None):
        super().__init__(parent)

        self.socket = socket

        self.initGraphicElements()
        self.initUI()
    
    def initGraphicsElements(self):
        self.radius = 6.0
        self._outline_width = 1.0

        self._background_color = QColor("#FFFF7700")
        self._outline_color = QColor("#FF000000")

        self._pen = QPen(self._outline_color)
        self._pen.setWidthF(self._outline_width)
        self._brush = QBrush(self._background_color)

    def initUI(self):
        self.is_drawing_bounding_box = True

    def boundingRect(self):
        return QRectF(
            -self.radius, 
            -self.radius, 
            2 * self.width,
            2 * self.height,
            ).normalized()

    def paint(self, painter, option, widget=None):
        
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

        if self.is_drawing_bounding_box:
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.drawRect(self.boundingRect())
