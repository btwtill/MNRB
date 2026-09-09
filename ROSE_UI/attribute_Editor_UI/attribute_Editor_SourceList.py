import os
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView, QSizePolicy #type: ignore
from PySide6.QtGui import QColor, QDrag #type: ignore
from PySide6.QtCore import Qt, QSize, QMimeData, QPoint #type: ignore
from MNRB.ROSE_UI.UI_GraphicComponents.list_group_item import List_Group_Item #type: ignore
from MNRB.ROSE_UI.UI_GraphicComponents.drag_payload import encodeIdNamePayload #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

dragdrop_log = ROSE_Log.get("rose.node_editor.dragdrop")

#separate mimetypes so an attribute can't be dropped where a control belongs
ATTRIBUTE_MIMETYPE = "application/x-rose-attribute"
CONTROL_MIMETYPE = "application/x-rose-control"

ENTRY_ID_ROLE = Qt.ItemDataRole.UserRole

GROUP_BACKGROUND = QColor(50, 50, 50)

class AttributeEditorSourceList(QListWidget):
    """Base for the tab's two source lists - exposed attributes on the left,
    controls on the right. Both are the same thing: entries grouped by component,
    dragged out onto an assignment box, so only the mimetype and where the
    entries come from actually differ.
    """

    mimetype = ATTRIBUTE_MIMETYPE
    #key inside each group dict holding the entry list (see NodeEditorScene's
    #getAttributeDict/getControlDict)
    entries_key = "attributes"

    def __init__(self, tab, parent = None):
        super().__init__(parent)

        self.tab = tab
        self.grouped_entries = {}

        self.initUI()

    def initUI(self):
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setMaximumWidth(260)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.buildRows()

    def buildRows(self):
        for key, group in self.grouped_entries.items():
            entries = group.get(self.entries_key, [])
            if not entries:
                continue

            base_item = QListWidgetItem(self)
            group_item = List_Group_Item(group.get("label", key), entries, self)
            group_item.setDragCallback(self.startGroupDrag)
            group_item.adjustSize()

            base_item.setSizeHint(group_item.sizeHint())
            base_item.setBackground(GROUP_BACKGROUND)
            self.setItemWidget(base_item, group_item)
            base_item.setFlags(base_item.flags() & ~Qt.ItemIsSelectable)

            for entry in entries:
                group_item.addListItem(self.addEntryItem(entry["name"], entry["id"]))

    def addEntryItem(self, name, entry_id):
        item = QListWidgetItem(name, self)
        item.setData(ENTRY_ID_ROLE, entry_id)
        item.setSizeHint(QSize(26, 26))
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled)
        return item

    def refresh(self, grouped_entries):
        #same scroll-preserving rebuild the skinning lists use - these refresh
        #whenever the graph changes, and losing the scroll position each time
        #makes a long list unusable
        scroll_position = self.verticalScrollBar().value()

        self.grouped_entries = grouped_entries
        self.clear()
        self.buildRows()

        self.updateGeometries()
        self.verticalScrollBar().setValue(scroll_position)

# Dragging

    def startDrag(self, *args, **kwargs):
        self.startDragForItems(self.selectedItems())

    def startGroupDrag(self, group_item):
        self.startDragForItems(group_item.list_items)

    def startDragForItems(self, items):
        if not items:
            return

        try:
            entries = [(item.data(ENTRY_ID_ROLE), item.text()) for item in items]

            mime_data = QMimeData()
            mime_data.setData(self.__class__.mimetype, encodeIdNamePayload(entries))

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(QPoint(0, 0))
            drag.exec_(Qt.CopyAction)

        except Exception as e:
            dragdrop_log.error("ATTRIBUTEEDITORSOURCELIST:: --startDragForItems:: ", e)


class AttributeEditorAttributeList(AttributeEditorSourceList):
    """Left pane - every attribute each component exposes, plus the rig-root
    attributes that belong to no component."""

    mimetype = ATTRIBUTE_MIMETYPE
    entries_key = "attributes"


class AttributeEditorControlList(AttributeEditorSourceList):
    """Right pane - every control in the rig, grouped by the component that owns
    it. Dragging one (or a whole component's worth) into the middle creates an
    assignment box for it."""

    mimetype = CONTROL_MIMETYPE
    entries_key = "controls"
