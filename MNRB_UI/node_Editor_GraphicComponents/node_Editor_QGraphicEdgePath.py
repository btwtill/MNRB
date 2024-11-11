from PySide2.QtCore import QPointF #type: ignore
from PySide2.QtGui import QPainterPath #type: ignore


class NodeEditor_QGraphicEdgePathBase():
    def __init__(self, parent):
        self.parent=parent

    def calculatePath(self):
        return None

class NodeEditor_QGaphicEdgePathDirect(NodeEditor_QGraphicEdgePathBase):
    def calculatePath(self):
        path = QPainterPath(QPointF(self.parent.source_position[0], self.parent.source_position[1]))
        path.lineTo(self.parent.destination_position[0], self.parent.destination_position[1])
        return path

class NodeEditor_QGraphicEdgePathBezier(NodeEditor_QGraphicEdgePathBase):
   def calculatePath(self):
        
        s = self.parent.source_position
        d = self.parent.destination_position
        dist = (d[0] - s[0]) * 0.5
        if s[0] > d[0]: dist *= -1

        path = QPainterPath(QPointF(self.parent.source_position[0], self.parent.source_position[1]))

        path.cubicTo( s[0] + dist, s[1], d[0] - dist, d[1],
            self.parent.destination_position[0], 
            self.parent.destination_position[1]
            )
        
        return path