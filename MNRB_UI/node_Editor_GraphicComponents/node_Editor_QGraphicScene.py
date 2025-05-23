import math
from PySide2 import QtWidgets # type: ignore
from PySide2.QtGui import QColor, QPen, QBrush # type: ignore
from PySide2.QtCore import QLine, QPoint, Qt, Signal # type: ignore

class NodeEditor_QGraphicScene(QtWidgets.QGraphicsScene):
    itemSelected = Signal()
    itemsDeselected = Signal()

    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.scene = scene

        self.initUI()
        
    def initUI(self):

        #Initilize Color variables
        self._backgroundColor = QColor("#2A2A2A")
        self._lightColor = QColor("#2E2E2E")
        self._darkColor = QColor("#1C1C1C")

        #initialize Pens for Drawing
        self._lightPen = QPen(self._lightColor)
        self._lightPen.setWidthF(2.0)
        self._darkPen = QPen(self._darkColor)
        self._darkPen.setWidthF(2.0)

        #initialize Brushes
        self.setBackgroundBrush(self._backgroundColor)
        self.centerPointBrush = QBrush(QColor("#020202"))

        #init Grid Values
        self._grid_Size = 20
        self._dark_Grid_Size = 5

    def setGrSceneSize(self, width, height):
        self.setSceneRect(-width / 2, -height / 2, width, height)

    #Has to be overriden otherwise draggin wont work
    def dragMoveEvent(self, event):
        pass

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        #set rectangle border Variables
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        firstLeft = left - left % self._grid_Size
        firstTop = top - top % self._grid_Size

        #initialize empty list that are gonna be drawn later
        light_Lines, dark_Lines = [], []

        #compute Light Lines
        for x in range(firstLeft, right, self._grid_Size):
           if x % (self._grid_Size * self._dark_Grid_Size) !=0 :
               light_Lines.append(QLine(x, top, x, bottom))
           else:
               dark_Lines.append(QLine(x, top, x, bottom))

        #compute Light Lines
        for y in range(firstTop, bottom, self._grid_Size):
            if y % (self._grid_Size * self._dark_Grid_Size) != 0 :
                light_Lines.append(QLine(left, y, right, y))
            else:
                dark_Lines.append(QLine(left, y, right, y))

        #draw Light Lines
        painter.setPen(self._lightPen)
        painter.drawLines(light_Lines)

        #draw Dark Lines
        painter.setPen(self._darkPen)
        painter.drawLines(dark_Lines)

        #drawCenterPoint 
        painter.setBrush(self.centerPointBrush)
        painter.drawEllipse(QPoint(-1800, -600), 3, 3)