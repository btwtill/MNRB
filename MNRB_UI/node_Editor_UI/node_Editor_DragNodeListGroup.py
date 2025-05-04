import os
from PySide2 import QtWidgets #type: ignore
from PySide2.QtGui import QColor #type: ignore


class NodeEditorDragNodeListGroup(QtWidgets.QListWidgetItem):
    def __init__(self, name, node_ids, parent = None):
        super().__init__(name, parent)

        self.node_ids = node_ids
        self.list_items = []

        self.initUI()

    def initUI(self):

        self.setBackground(QColor(50, 50, 50))

    def addListItem(self, item):
        self.list_items.append(item)

    def onClick(self):
        print("NodeEditorDragNodeListGroup:: --onClick:: GroupName:: ")