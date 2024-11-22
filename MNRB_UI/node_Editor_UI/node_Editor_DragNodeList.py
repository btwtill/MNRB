import os
from PySide2 import QtWidgets #type: ignore
from PySide2.QtCore import QSize, Qt #type: ignore
from PySide2.QtGui import QPixmap, QIcon #type: ignore
from MNRB.MNRB_UI.node_Editor_conf import OPERATION_BASECOMPONENT, OPERATION_TESTCOMPONENT #type: ignore

ICONPATH = os.path.join(os.path.dirname(__file__), "../icons")

DRAGDROP_DEBUG = True

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
        self.addDragListItem("BaseComponent", os.path.join(ICONPATH, "base_component.png"), OPERATION_BASECOMPONENT)
        self.addDragListItem("TestNode", operation_code=OPERATION_TESTCOMPONENT)

    def addDragListItem(self, name, icon=None, operation_code=0):
        item = QtWidgets.QListWidgetItem(name, self)

        icon_pixmap = QPixmap(icon if icon is not None else ".")
        item.setIcon(QIcon(icon_pixmap))
        item.setSizeHint(QSize(32,32))

        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)

        item.setData(Qt.ItemDataRole.UserRole, icon_pixmap)
        item.setData(Qt.ItemDataRole.UserRole + 1, operation_code)

    def startDrag(self, *args, **kwargs):
        if DRAGDROP_DEBUG: print("NODEDRAGLIST:: --startDrag:: ")

        try:
            item = self.currentItem()
            operation_code = item.data(Qt.ItemDataRole.UserRole + 1)
            if DRAGDROP_DEBUG: print("NODEDRAGLIST:: --startDrag:: Item:: OperationCode:: ", operation_code, " Class:: ", item )


        except Exception as e:
            print(e)