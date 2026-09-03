import os
from PySide6.QtWidgets import QListWidget, QSizePolicy, QListWidgetItem, QAbstractItemView #type: ignore
from PySide6.QtGui import QColor, QPixmap, QIcon, QDrag #type: ignore
from PySide6.QtCore import QSize, Qt, QMimeData, QByteArray, QDataStream, QIODevice, QPoint #type: ignore
from MNRB.ROSE_UI.UI_GraphicComponents.list_group_item import List_Group_Item #type: ignore

ICONPATH = os.path.join(os.path.dirname(__file__), "../icons")

#dragging a deform from this list onto a skinCluster container box - mirrors
#NODELIST_MIMETYPE's usage in node_Editor_DragNodeList.py
SKINDEFORM_MIMETYPE = "application/x-rose-skindeform"

DRAGDROP_DEBUG = False

STATUS_NORMAL = "normal"
STATUS_ADDED = "added"
STATUS_REMOVED = "removed"

ADDED_COLOR = QColor("#FF2E6B2E")
REMOVED_COLOR = QColor("#FF6B2E2E")

class SkinningEditorDeformList(QListWidget):
    def __init__(self, deformer_dict = {}, parent=None):
        super().__init__(parent)
        self.tab = parent
        self.deformer_dict = deformer_dict
        #{component_prefix: [{"id", "name", "status"}, ...]} - unlike deformer_dict,
        #this persists across updates so a deform that disappeared from the node
        #graph keeps showing here (status=removed) until explicitly cleared via
        #the "Remove Deprecated" button, rather than just vanishing silently
        self.tracked_dict = {}
        self.initUI()

    def initUI(self):
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setMaximumWidth(250)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)

        for key in self.tracked_dict.keys():
            base_item = QListWidgetItem(self)
            list_group_item = List_Group_Item(key, self.tracked_dict[key], self)
            list_group_item.adjustSize()
            base_item.setSizeHint(list_group_item.sizeHint())
            base_item.setBackground(QColor(50, 50, 50))

            self.setItemWidget(base_item, list_group_item)
            base_item.setFlags(base_item.flags() & ~Qt.ItemIsSelectable)

            for entry in self.tracked_dict[key]:
                item = self.addDragListItem(entry["name"], entry["id"], entry["status"], "")
                list_group_item.addListItem(item)

    def addDragListItem(self, name, deform_id, status = STATUS_NORMAL, icon=None):
        item = QListWidgetItem(name, self)

        icon_str = icon if icon is not None else ""
        icon_path = os.path.join(ICONPATH, icon_str)
        icon_pixmap = QPixmap(icon_path if icon_str != "" else os.path.join(ICONPATH, "default_node.png"))
        item.setIcon(QIcon(icon_pixmap))
        item.setSizeHint(QSize(32,32))

        item.setData(Qt.ItemDataRole.UserRole, deform_id)

        if status == STATUS_REMOVED:
            item.setBackground(REMOVED_COLOR)
            #no longer exists in the graph - nothing to resolve on the other end
            #of a drop, so don't offer it as draggable
        elif status == STATUS_ADDED:
            item.setBackground(ADDED_COLOR)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled)
        else:
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled)

        return item

    def startDrag(self, *args, **kwargs):
        if DRAGDROP_DEBUG: print("SKINNINGDEFORMLIST:: --startDrag:: ")

        try:
            item = self.currentItem()
            deform_id = item.data(Qt.ItemDataRole.UserRole)

            item_data = QByteArray()
            data_stream = QDataStream(item_data, QIODevice.WriteOnly)
            data_stream.writeInt64(deform_id)
            data_stream.writeQString(item.text())

            mime_data = QMimeData()
            mime_data.setData(SKINDEFORM_MIMETYPE, item_data)

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(QPoint(0, 0))

            drag.exec_(Qt.MoveAction)

        except Exception as e:
            print(e)

    def updateDeformerList(self, deformer_dict):
        self.deformer_dict = deformer_dict
        self.tracked_dict = self.mergeTrackedState(self.tracked_dict, deformer_dict)
        self.clear()
        self.initUI()
        self.tab.updateRemoveDeprecatedButtonState()
        self.tab.updateAcceptNewButtonState()

    def mergeTrackedState(self, old_tracked, new_dict):
        merged = {}

        for component in set(old_tracked.keys()) | set(new_dict.keys()):
            old_entries = old_tracked.get(component, [])
            new_entries = new_dict.get(component, [])

            old_by_id = {entry["id"]: entry for entry in old_entries}
            #first entry wins on a name collision - shouldn't happen in practice,
            #deform names are deterministic per component/guide slot
            old_by_name = {}
            for entry in old_entries:
                old_by_name.setdefault(entry["name"], entry)

            matched_old_ids = set()
            merged_entries = []

            for entry in new_entries:
                #id first (survives a rename - same deform object, new name),
                #falling back to name (survives a static rebuild, which recreates
                #the deform object with a fresh id but a deterministic, usually-
                #identical name) - same hybrid resolution
                #SkinningEditorCluster.resolveDeforms() already relies on. Without
                #this fallback, every rebuild looked like every deform got removed
                #and a same-named one got added right back.
                previous = old_by_id.get(entry["id"]) or old_by_name.get(entry["name"])

                if previous is not None:
                    matched_old_ids.add(previous["id"])

                if previous is not None and previous["status"] != STATUS_REMOVED:
                    #existed before (found via id or name) - keep whatever status
                    #it already had. "added" stays green until explicitly accepted
                    #rather than auto-clearing after one refresh, same persistence
                    #"removed" already has.
                    status = previous["status"]
                else:
                    status = STATUS_ADDED

                merged_entries.append({"id": entry["id"], "name": entry["name"], "status": status})

            for entry in old_entries:
                if entry["id"] not in matched_old_ids:
                    #genuinely gone - neither id nor name resolved against the
                    #current graph pull. Keep showing it, marked removed, until
                    #the user explicitly clears it.
                    merged_entries.append({"id": entry["id"], "name": entry["name"], "status": STATUS_REMOVED})

            if merged_entries:
                merged[component] = merged_entries

        return merged

    def hasDeprecatedEntries(self):
        return any(entry["status"] == STATUS_REMOVED for entries in self.tracked_dict.values() for entry in entries)

    def hasNewEntries(self):
        return any(entry["status"] == STATUS_ADDED for entries in self.tracked_dict.values() for entry in entries)

    def clearDeprecatedEntries(self):
        cleaned = {}
        for component, entries in self.tracked_dict.items():
            remaining = [entry for entry in entries if entry["status"] != STATUS_REMOVED]
            if remaining:
                cleaned[component] = remaining
        self.tracked_dict = cleaned
        self.clear()
        self.initUI()

    def acceptNewEntries(self):
        for entries in self.tracked_dict.values():
            for entry in entries:
                if entry["status"] == STATUS_ADDED:
                    entry["status"] = STATUS_NORMAL
        self.clear()
        self.initUI()
