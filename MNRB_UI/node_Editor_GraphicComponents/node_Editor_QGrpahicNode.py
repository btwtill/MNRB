from PySide2 import QtWidgets # type:ignore
from PySide2.QtCore import Qt, QRectF # type: ignore
from PySide2.QtGui import QFont, QBrush, QPen # type: ignore




class NodeEditor_QGraphicNode(QtWidgets.QGraphicsItem):
    def __init__(self, node, parent = None):
        super().__init__(parent)

        self.node = node

        self._size = 40
    
        self.initGraphicElements()
        self.initUI()

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self.title)

    def initUI(self):
        pass
    
    def initGraphicElements(self):
        #initialize the variables for the Graphical Elements
        self._title_color = Qt.white
        self._title_font = QFont("Helvetica", 10)

        #initialize the node title
        self.title_item = QtWidgets.QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title = self.node.title

    def boundingRect(self):
        return QRectF(0, 0, self._size, self._size)

    # Paint method to draw the square
    def paint(self, painter, option, widget=None):
        painter.setBrush(QBrush(Qt.blue))  # Fill color
        painter.setPen(QPen(Qt.black, 2))  # Border color and thickness
        painter.drawRect(0, 0, self._size, self._size)    # Draw the square
