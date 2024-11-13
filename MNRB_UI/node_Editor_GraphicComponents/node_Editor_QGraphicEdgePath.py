import math
from PySide2.QtCore import QPointF #type: ignore
from PySide2.QtGui import QPainterPath #type: ignore

EDGE_CP_ROUNDNESS = 100

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
        
        dist = (self.parent.destination_position[0] - self.parent.source_position[0]) * 0.5

        cpxSource = +dist
        cpxDestination = -dist
        cpySource = 0
        cpyDestination = 0



        if self.parent.edge.start_socket is not None:

            is_start_socket_input = self.parent.edge.start_socket.is_input
            is_start_socket_output = self.parent.edge.start_socket.is_output

            if self.parent.source_position[0] > self.parent.destination_position[0] and is_start_socket_output or self.parent.source_position[0] < self.parent.destination_position[0] and is_start_socket_input:
                
                cpxDestination *= -1
                cpxSource *= -1
                
                cpyDestination = (
                        (self.parent.source_position[1] - self.parent.destination_position[1]) / math.fabs(
                    (self.parent.source_position[1] - self.parent.destination_position[1]) if (self.parent.source_position[1] -
                                                                        self.parent.destination_position[1]) != 0 else 0.00001)
                ) * EDGE_CP_ROUNDNESS

                cpySource = (
                        (self.parent.destination_position[1] - self.parent.source_position[1]) / math.fabs(
                    (self.parent.destination_position[1] - self.parent.source_position[1]) if (self.parent.destination_position[1] -
                                                                        self.parent.source_position[1]) != 0 else 0.00001)
                ) * EDGE_CP_ROUNDNESS

        path = QPainterPath(QPointF(self.parent.source_position[0], self.parent.source_position[1]))

        path.cubicTo(
            self.parent.source_position[0] + cpxSource, 
            self.parent.source_position[1] + cpySource,
            self.parent.destination_position[0] + cpxDestination, 
            self.parent.destination_position[1] + cpyDestination,
            self.parent.destination_position[0], 
            self.parent.destination_position[1]
            )
        
        return path