from PySide2 import QtWidgets #type: ignore
from PySide2.QtCore import Qt #type: ignore
from PySide2.QtGui import QColor, QPen, QPainterPath #type: ignore
from MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdgePath import  NodeEditor_QGaphicEdgePathDirect, NodeEditor_QGraphicEdgePathBezier #type: ignore

SELECTION_DEBUG = True
INTERSECT_DEBUG = False

class NodeEditor_QGraphicEdge(QtWidgets.QGraphicsPathItem):
    def __init__(self, edge, parent = None):
        super().__init__(parent)

        self.edge = edge
        self.edge_path_calculator = self.determin_edge_path_class()(self)

        self._last_selected_state = False

        self.source_position = [0, 0]
        self.destination_position = [0, 0]

        self.initUI()
        self.initGraphicElements()

    def initUI(self):
        #set QItem Flags
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.is_drawing_bounding_box = False
        self.setZValue(-1)

    def initGraphicElements(self):
        #path edge colors
        self._default_color = QColor("#000000")
        self._selected_color = QColor("#FFFFA637")

        #path edge pens
        self._default_pen = QPen(self._default_color)
        self._default_pen.setWidthF(2.0)
        self._selected_pen = QPen(self._selected_color)
        self._selected_pen.setWidthF(2.0)
        self._dragging_pen = QPen(self._default_color)
        self._dragging_pen.setWidthF(2.0)
        self._dragging_pen.setStyle(Qt.DashLine)
       
    def determin_edge_path_class(self):
        #sort out what subcluss should be created as the path calculator to use there calculate path method and draw that path
        from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge import EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER #type: ignore
        if self.edge.edge_type == EDGE_TYPE_BEZIER:
            return  NodeEditor_QGraphicEdgePathBezier
        if self.edge.edge_type == EDGE_TYPE_DIRECT:
            return NodeEditor_QGaphicEdgePathDirect

    def createEdgePathCalculator(self):
        self.edge_path_calculator = self.determin_edge_path_class()(self)
        return self.edge_path_calculator

    def calculatePath(self):
        return self.edge_path_calculator.calculatePath()

    def intersectsWith(self, point1, point2):
        if INTERSECT_DEBUG: print("GRAPHICEDGE:: --intersectsWith:: Checking for Intersection:: Edge: ", self, " with Point 1", point1, " and Point2 ", point2)
        cut_path = QPainterPath(point1)
        cut_path.lineTo(point2)
        path = self.calculatePath()
        result = cut_path.intersects(path)
        if INTERSECT_DEBUG: print("GRAPHICEDGE:: --intersectsWith:: Intersection With Edge:: ", result)
    
        return result

    def onSelected(self):
        if SELECTION_DEBUG: print("GRAPHICEDGE:: --onSelected:: ")
        self.edge.scene.grScene.itemSelected.emit()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self._last_selected_state != self.isSelected():
            self.edge.scene.reset_last_selected_states()
            self._last_selected_state = self.isSelected()
            self.onSelected()
            self.edge.scene._last_selected_items = self.edge.scene.getSelectedItems()

    def setSourceSocketPosition(self, x, y):
        self.source_position = [x, y]
    
    def setDestinationSocketPosition(self, x, y):
        self.destination_position = [x, y]

    #causing access viloation in some cases
    # def boundingRect(self):
    #     return self.shape().boundingRect()
    
    def shape(self):
        return self.calculatePath()

    def paint(self, painter, options, widget=None):
        #get path from the path calculator
        self.setPath(self.calculatePath())

        #paint the edge
        if self.edge.end_socket is None:
            painter.setPen(self._dragging_pen)
        else:
            painter.setPen(self._default_pen if not self.isSelected() else self._selected_color)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

        #drawing the bounding box of the path
        if self.is_drawing_bounding_box:
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.boundingRect())

    def __str__(self): return "ClassInstance::%s::  %s..%s" % (__class__.__name__, hex(id(self))[2:5], hex(id(self))[-3:])
