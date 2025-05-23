import os
from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel #type: ignore
from PySide2.QtGui import QColor, QIcon #type: ignore
from MNRB.MNRB_UI.UI_GraphicComponents.triangleWidget import TriangleWidget #type: ignore

class List_Group_Item(QWidget):
    def __init__(self, name, item_ids, parent = None):
        super().__init__(parent)

        self.item_ids = item_ids
        self.name = name
        self.list_items = []

        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout(self)
        
        self.layout.setContentsMargins(10,10,10,10)  # Add some padding
        self.layout.setSpacing(10)

        self.triangle_widget = TriangleWidget(self)
        self.triangle_widget.setFixedSize(20, 20)
        self.triangle_widget.setColor(QColor("#FF181818"))
        self.title = QLabel(self.name)

        self.layout.addWidget(self.triangle_widget)
        self.layout.addWidget(self.title)

        self.setLayout(self.layout)

        self.triangle_widget.rotate()

    def addListItem(self, item):
        self.list_items.append(item)

    def mousePressEvent(self, event):
        for node_list_item in self.list_items:
            if node_list_item.isHidden():
                node_list_item.setHidden(False)
            else:
                node_list_item.setHidden(True)
        self.triangle_widget.rotate()
        self.triangle_widget.update()
        super().mousePressEvent(event)