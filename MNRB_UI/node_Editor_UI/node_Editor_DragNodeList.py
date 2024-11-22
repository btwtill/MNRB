import os
from PySide2 import QtWidgets #type: ignore
from PySide2.QtCore import QSize, Qt #type: ignore
from PySide2.QtGui import QPixmap, QIcon #type: ignore

ICONPATH = os.path.join(os.path.dirname(__file__), "../icons")

class NodeEditorDragNodeList(QtWidgets.QListWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.initUI()

    def initUI(self):
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        self.setBaseSize(QSize(150, 600))
        self.setMaximumWidth(200)

        self.addDragListItems()
        
    def addDragListItems(self):
        self.addDragListItem("BaseComponent", os.path.join(ICONPATH, "base_component.png"))
        self.addDragListItem("TestNode")

    def addDragListItem(self, name, icon=None, operation_code=0):
        item = QtWidgets.QListWidgetItem(name, self)

        icon_pixmap = QPixmap(icon if icon is not None else ".")
        item.setIcon(QIcon(icon_pixmap))
        item.setSizeHint(QSize(32,32))

        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)

        item.setData(Qt.ItemDataRole.UserRole, icon_pixmap)
        item.setData(Qt.ItemDataRole.UserRole + 1, operation_code)