from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdgePath import  NodeEditor_QGaphicEdgePathDirect, NodeEditor_QGraphicEdgePathBezier #type: ignore
from PySide2 import QtWidgets #type: ignore
from PySide2.QtCore import Qt #type: ignore

class NodeEditor_QGraphicEdge(QtWidgets.QGraphicsPathItem):
    def __init__(self, edge, parent = None):
        super().__init__(parent)

        self.edge = edge
        self.edge_path_calculator = self.determin_edge_path_class()(self)
        
    def determin_edge_path_class(self):
        from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge import EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER #type: ignore
        if self.edge.edge_type == EDGE_TYPE_BEZIER:
            return  NodeEditor_QGraphicEdgePathBezier
        if self.edge.edge_type == EDGE_TYPE_DIRECT:
            return NodeEditor_QGaphicEdgePathDirect

    def calculatePath(self):
        self.edge_path_calculator.calculatePath()

    def paint(self, painter, options, widget=None):
        self.calculatePath()

        painter.setPen(self._pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())
