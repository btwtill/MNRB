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

    @property
    def title(self): return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self.title)

    @property
    def content(self): return self.node.content if self.node else None

    def initGraphicElements(self):
        #initialize Graphic element variables
        self._min_width = 100
        self._min_height = 60
        self.width, self.height = self.calculateGrNodeSize(self.node.inputs, self.node.outputs)
        self._edge_roundness = 5
        self._edge_padding = 5
        self._title_height = 20

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
            self.content.setGeometry(self._edge_padding, self._title_height + self._edge_padding, self.width - 2 * self._edge_padding, self.height - 2 *  self._edge_padding - self._title_height )

        self.grContent = self.node.scene.grScene.addWidget(self.content)
        self.grContent.setParentItem(self)

    def initUI(self):
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)

        self.is_drawing_bounding_box = False
    
    def setIsDrawingBoundingBox(self, value=True):
        self.is_drawing_bounding_box = value

    def calculateGrNodeSize(self, inputs, outputs):
        socket_padding = 40
        max_height = (len(inputs) * socket_padding) + (len(outputs) * socket_padding) + self._min_height
        max_width = self._min_width
        return max_width, max_height

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
        path_title.addRoundedRect(0,0, self.width, self._title_height, self._edge_roundness, self._edge_roundness)
        path_title.addRect(0, self._title_height -self._edge_roundness, self._edge_roundness, self._edge_roundness)
        path_title.addRect(self.width - self._edge_roundness, self._title_height -self._edge_roundness, self._edge_roundness, self._edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._title_background_brush)
        painter.drawPath(path_title.simplified())

        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self._title_height, self.width, self.height - self._title_height, self._edge_roundness, self._edge_roundness)
        path_content.addRect(0, self._title_height, self._edge_roundness, self._edge_roundness)
        path_content.addRect(self.width - self._edge_roundness, self._title_height, self._edge_roundness, self._edge_roundness)
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