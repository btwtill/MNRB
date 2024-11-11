from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdgePath import  NodeEditor_QGaphicEdgePathDirect, NodeEditor_QGraphicEdgePathBezier #type: ignore
from PySide2 import QtWidgets #type: ignore
from PySide2.QtCore import Qt #type: ignore
from PySide2.QtGui import QColor, QPen #type: ignore

class NodeEditor_QGraphicEdge(QtWidgets.QGraphicsPathItem):
    def __init__(self, edge, parent = None):
        super().__init__(parent)

        self.edge = edge
        self.edge_path_calculator = self.determin_edge_path_class()(self)

        self.source_position = [0, 0]
        self.destination_position = [150, 200]

        self.initGraphicElements()

    def initGraphicElements(self):
        
        #path edge colors
        self._default_color = QColor("#001000")

        #path edge pens
        self._default_pen = QPen(self._default_color)
       
    def determin_edge_path_class(self):
        #sort out what subcluss should be created as the path calculator to use there calculate path method and draw that path
        from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge import EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER #type: ignore
        if self.edge.edge_type == EDGE_TYPE_BEZIER:
            return  NodeEditor_QGraphicEdgePathBezier
        if self.edge.edge_type == EDGE_TYPE_DIRECT:
            return NodeEditor_QGaphicEdgePathDirect

    def calculatePath(self):
        return self.edge_path_calculator.calculatePath()

    def paint(self, painter, options, widget=None):
        self.setPath(self.calculatePath())

        painter.setPen(self._default_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())
