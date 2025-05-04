from PySide2.QtWidgets import QWidget, QSizePolicy #type: ignore
from PySide2.QtGui import QPainter, QPolygon, QBrush, QColor #type: ignore
from PySide2.QtCore import Qt, QPoint #type: ignore

class TriangleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.color = QColor('#2B2B2B')

        self.is_rotated = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Define the triangle points
        if self.is_rotated:
            triangle = QPolygon([
                QPoint(0, 2), #upper left
                QPoint(self.width() - 5, 2), #upper right
                QPoint((self.width() // 2) - 2, self.height() - 2) #bottom center
            ])
        else:
            triangle = QPolygon([
                QPoint(0, 2),  # Upper Left
                QPoint(self.width() - 5, self.height() // 2),  # right center
                QPoint(0, self.height() - 2)  # bottom left
            ])

        # Set the brush and pen
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.NoPen)

        # Draw the triangle
        painter.drawPolygon(triangle)

    def rotate(self):
        self.is_rotated = not self.is_rotated

    def setColor(self, color):
        self.color = color