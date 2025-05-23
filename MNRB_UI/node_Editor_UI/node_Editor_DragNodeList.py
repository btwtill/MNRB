import os
from PySide2 import QtWidgets #type: ignore
from PySide2.QtCore import QSize, Qt, QMimeData, QByteArray, QDataStream, QIODevice, QPoint #type: ignore
from PySide2.QtGui import QPixmap, QIcon, QDrag, QColor #type: ignore
from MNRB.MNRB_Nodes.node_Editor_conf import NODELIST_MIMETYPE, MNRB_NODES, MNRB_NODE_GROUPS, getClassFromOperationCode #type: ignore
from MNRB.MNRB_UI.UI_GraphicComponents.list_group_item import List_Group_Item #type: ignore

ICONPATH = os.path.join(os.path.dirname(__file__), "../icons")

DRAGDROP_DEBUG = False
CLASS_DEBUG = False

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

        if CLASS_DEBUG: print("DRAGNODELIST:: --addDragListItems:: Registered Items::", MNRB_NODES)

        node_groups = MNRB_NODE_GROUPS

        for group_id in node_groups.keys():
            # add group item
            base_item = QtWidgets.QListWidgetItem(self)
            group_widget = self.addDragListGroupItem(node_groups[group_id][0], node_groups[group_id][1])
            group_widget.adjustSize()
            base_item.setSizeHint(group_widget.sizeHint())
            base_item.setBackground(QColor(50, 50, 50))

            self.setItemWidget(base_item, group_widget)

            # add nodes associated with the group
            for node_id in node_groups[group_id][1]:
                node = getClassFromOperationCode(node_id)
                item = self.addDragListItem(node.operation_title, node.icon, node.operation_code)
                group_widget.addListItem(item)

    def addDragListItem(self, name, icon=None, operation_code=0):
        item = QtWidgets.QListWidgetItem(name, self)

        icon_path = os.path.join(ICONPATH, icon)
        icon_pixmap = QPixmap(icon_path if icon != "" else os.path.join(ICONPATH, "default_node.png"))
        item.setIcon(QIcon(icon_pixmap))
        item.setSizeHint(QSize(32,32))

        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)

        item.setData(Qt.ItemDataRole.UserRole, icon_pixmap)
        item.setData(Qt.ItemDataRole.UserRole + 1, operation_code)

        return item

    def addDragListGroupItem(self, group_name, node_ids):
        print("DRAGNODELIST:: --addDragListGroupItem:: GroupName:: ", group_name, " NodeIDs:: ", node_ids)
        item = List_Group_Item(group_name, node_ids, self)

        return item

    def startDrag(self, *args, **kwargs):
        if DRAGDROP_DEBUG: print("NODEDRAGLIST:: --startDrag:: ")

        try:
            item = self.currentItem()
            operation_code = item.data(Qt.ItemDataRole.UserRole + 1)

            if DRAGDROP_DEBUG: print("NODEDRAGLIST:: --startDrag:: Item:: OperationCode:: ", operation_code, " Class:: ", item)

            icon_pixmap = QPixmap(item.data(Qt.ItemDataRole.UserRole))

            item_data = QByteArray()
            data_stream = QDataStream(item_data, QIODevice.WriteOnly)
            data_stream << icon_pixmap
            data_stream.writeInt32(operation_code)
            data_stream.writeQString(item.text())

            mime_data = QMimeData()
            mime_data.setData(NODELIST_MIMETYPE, item_data)

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(QPoint(icon_pixmap.width() / 2, icon_pixmap.height() / 2))
            drag.setPixmap(icon_pixmap)

            drag.exec_(Qt.MoveAction)

        except Exception as e:
            print(e)