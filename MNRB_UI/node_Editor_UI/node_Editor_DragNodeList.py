from PySide2 import QtWidgets #type: ignore
from PySide2.QtCore import QSize #type: ignore

class NodeEditorDragNodeList(QtWidgets.QListWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)

        self.addDragListItems()
        
    def addDragListItems(self):
        for item in range(4):
            self.addDragListItem()

    def addDragListItem(self):
        item = QtWidgets.QListWidgetItem("test", self)