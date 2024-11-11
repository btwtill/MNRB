from PySide2 import QtWidgets # type:ignore
from PySide2.QtCore import Qt, QRectF # type: ignore
from PySide2.QtGui import QFont, QBrush, QPen, QColor, QPainterPath # type: ignore



class NodeEditor_QGraphicNode(QtWidgets.QGraphicsItem):
    def __init__(self, node, parent = None):
        super().__init__(parent)

        self.node = node

        self.initGraphicElements()
        self.initContent()
        self.initUI()
        self.wrapGrNodeToSockets()

    @property
    def title(self): return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self.title)

    @property
    def content(self): return self.node.content if self.node else None

    @property
    def width(self): return self._width

    @width.setter
    def width(self, value):
            self._width = value

    @property
    def height(self): return self._height

    @height.setter
    def height(self, value):
        if value >= 60:
            self._height = value
        else:
            self._height = 60

    def initGraphicElements(self):
        #initialize Graphic element variables
        self.width = 100
        self.height = 60

        self.socket_padding = 12.0
        self.socket_radius = 5.0

        self._edge_roundness = 5
        self._edge_padding = 5

        self.title_height = 20

        #initialize the variables for the Graphical Elements
        self._title_font = QFont("Helvetica", 8)
        self._title_padding = 10

        self._default_color = QColor("#7F000000")
        self._selected_color = QColor("#FFFFA637")
        self._title_color = Qt.white
        self._title_backgroundColor = QColor("#FF181818")
        self._content_color = QColor("#EF1F1F1F")

        self._default_pen = QPen(self._default_color)
        self._selected_pen = QPen(self._selected_color)

        self._title_background_brush = QBrush(self._title_backgroundColor)
        self._content_brush = QBrush(self._content_color)

        #initialize the node title
        self.title_item = QtWidgets.QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._title_padding, 0)
        self.title_item.setTextWidth(
            self.width  - 2 * self._title_padding
        )
        self.title = self.node.title

    def initContent(self):
        if self.content is not None:
            self.content.setGeometry(self._edge_padding, self.title_height + self._edge_padding, self.width - 2 * self._edge_padding, self.height - 2 *  self._edge_padding - self.title_height )

        self.grContent = self.node.scene.grScene.addWidget(self.content)
        self.grContent.setParentItem(self)

    def initUI(self):
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)

        self.is_drawing_bounding_box = False
    
    def setIsDrawingBoundingBox(self, value=True):
        self.is_drawing_bounding_box = value

    def wrapGrNodeToSockets(self):
        full_socket_height = self.socket_padding + self.socket_radius
        full_node_length = (len(self.node.inputs) * full_socket_height) + (len(self.node.outputs) * full_socket_height) + self.title_height + self.socket_padding
        self.height = full_node_length

    def boundingRect(self):
        return QRectF(
            0, 
            0, 
            self.width,
            self.height,
            ).normalized()

    # Paint method to draw the square
    def paint(self, painter, option, widget=None):

        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0,0, self.width, self.title_height, self._edge_roundness, self._edge_roundness)
        path_title.addRect(0, self.title_height -self._edge_roundness, self._edge_roundness, self._edge_roundness)
        path_title.addRect(self.width - self._edge_roundness, self.title_height -self._edge_roundness, self._edge_roundness, self._edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._title_background_brush)
        painter.drawPath(path_title.simplified())

        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self._edge_roundness, self._edge_roundness)
        path_content.addRect(0, self.title_height, self._edge_roundness, self._edge_roundness)
        path_content.addRect(self.width - self._edge_roundness, self.title_height, self._edge_roundness, self._edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._content_brush)
        painter.drawPath(path_content.simplified())

        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self._edge_roundness, self._edge_roundness)
        painter.setPen(self._default_pen if not self.isSelected() else self._selected_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())
        
        #paintBounding Rect
        if self.is_drawing_bounding_box:
            painter.setPen(QPen(Qt.red, 1, Qt.DashLine))
            painter.drawRect(self.boundingRect())