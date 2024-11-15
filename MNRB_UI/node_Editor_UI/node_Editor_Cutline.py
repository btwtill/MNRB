from PySide2 import QtWidgets #type: ignore
from PySide2.QtGui import QPen, QPainter, QPolygonF, QPainterPath #type: ignore
from PySide2.QtCore import Qt, QPointF #type: ignore

class NodeEditorCutLine(QtWidgets.QGraphicsItem):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.line_points = []

        self._pen = QPen(Qt.white)
        self._pen.setWidthF(2.0)
        self._pen.setDashPattern([3, 3])

        self.setZValue(2)

        self.is_drawing_bounding_box = False

    def boundingRect(self):
        return self.shape().boundingRect()
    
    def shape(self):

        poly = QPolygonF(self.line_points)

        if len(self.line_points) > 1:
            path = QPainterPath(self.line_points[0])
            for pt in self.line_points[1:]:
                path.lineTo(pt)
        else:
            path = QPainterPath(QPointF(0,0))
            path.lineTo(QPointF(1,1))

        return path
    
    def paint(self, painter, options, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.line_points)
        painter.drawPolyline(poly)

        if self.is_drawing_bounding_box:
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.drawRect(self.boundingRect())

