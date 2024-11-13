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

        cpx_source = +dist
        cpx_destination = -dist
        cpy_source = 0
        cpy_destination = 0

        if self.parent.edge.start_socket is not None:
            
            is_start_socket_input = self.parent.edge.start_socket.is_input
            is_start_socket_output = self.parent.edge.start_socket.is_output

            #if the sockets are not input on the left screen side and output on the right screen side flip the X component of the control points
            if self.parent.source_position[0] > self.parent.destination_position[0] and is_start_socket_output or self.parent.source_position[0] < self.parent.destination_position[0] and is_start_socket_input:
                
                #inverting the X position of the control points
                cpx_destination *= -1
                cpx_source *= -1
                
                cpy_destination = (
                        (self.parent.source_position[1] - self.parent.destination_position[1]) / math.fabs(
                    (self.parent.source_position[1] - self.parent.destination_position[1]) if (self.parent.source_position[1] -
                                                                        self.parent.destination_position[1]) != 0 else 0.00001)
                ) * EDGE_CP_ROUNDNESS

                cpy_source = (
                        (self.parent.destination_position[1] - self.parent.source_position[1]) / math.fabs(
                    (self.parent.destination_position[1] - self.parent.source_position[1]) if (self.parent.destination_position[1] -
                                                                        self.parent.source_position[1]) != 0 else 0.00001)
                ) * EDGE_CP_ROUNDNESS


        #path start Position
        path = QPainterPath(QPointF(self.parent.source_position[0], self.parent.source_position[1]))

        #adding final position with a cubic interpolation
        path.cubicTo(
            self.parent.source_position[0] + cpx_source, 
            self.parent.source_position[1] + cpy_source,
            self.parent.destination_position[0] + cpx_destination, 
            self.parent.destination_position[1] + cpy_destination,
            self.parent.destination_position[0], 
            self.parent.destination_position[1]
            )
        
        return path