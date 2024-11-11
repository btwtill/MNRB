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
        return None