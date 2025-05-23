import os
from PySide2.QtWidgets import QListWidget, QSizePolicy, QListWidgetItem #type: ignore
from PySide2.QtGui import QColor, QPixmap, QIcon  #type: ignore
from PySide2.QtCore import QSize #type: ignore
from MNRB.MNRB_UI.UI_GraphicComponents.list_group_item import List_Group_Item #type: ignore

ICONPATH = os.path.join(os.path.dirname(__file__), "../icons")

class SkinningEditorDeformList(QListWidget):
    def __init__(self, deformer_dict = {}, parent=None):
        super().__init__(parent)
        self.tab = parent
        self.deformer_dict = deformer_dict
        self.initUI()

    def initUI(self):
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setMaximumWidth(250)
        print(self.deformer_dict)
        for key in self.deformer_dict.keys():

            base_item = QListWidgetItem(self)
            list_group_item = List_Group_Item(key, self.deformer_dict[key], self)
            list_group_item.adjustSize()
            base_item.setSizeHint(list_group_item.sizeHint())
            base_item.setBackground(QColor(50, 50, 50))

            self.setItemWidget(base_item, list_group_item)

            for value in self.deformer_dict[key]:
                item = self.addDragListItem(value, "")
                list_group_item.addListItem(item)

    def addDragListItem(self, name, icon=None):
        item = QListWidgetItem(name, self)

        icon_str = icon if icon is not None else ""
        icon_path = os.path.join(ICONPATH, icon_str)
        icon_pixmap = QPixmap(icon_path if icon_str != "" else os.path.join(ICONPATH, "default_node.png"))
        item.setIcon(QIcon(icon_pixmap))
        item.setSizeHint(QSize(32,32))

        return item
    
    def updateDeformerList(self, deformer_dict):
        self.deformer_dict = deformer_dict
        self.clear()
        self.initUI()