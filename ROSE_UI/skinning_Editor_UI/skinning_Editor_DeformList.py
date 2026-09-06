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

#status is carried alongside the id so a drag can filter out deforms that no
#longer resolve, without inferring it back out of the item's flags/background
DEFORM_ID_ROLE = Qt.ItemDataRole.UserRole
DEFORM_STATUS_ROLE = Qt.ItemDataRole.UserRole + 1

#a group is {"label": <component prefix>, "deforms": [entry, ...]}. Projects saved
#before the grouping moved off the component prefix stored a bare entry list keyed
#by that prefix, so both shapes are read here
def getGroupEntries(group):
    if isinstance(group, dict):
        return group.get("deforms", [])
    return group

def getGroupLabel(key, group):
    if isinstance(group, dict):
        return group.get("label", key)
    return key

def encodeDeformPayload(deform_entries):
    """deform_entries: a list of (deform_id, deform_name).

    Count-prefixed, so one drag carries a whole multi selection or a whole group
    just as easily as a single row.
    """
    payload = QByteArray()
    data_stream = QDataStream(payload, QIODevice.WriteOnly)

    data_stream.writeInt32(len(deform_entries))
    for deform_id, deform_name in deform_entries:
        data_stream.writeInt64(deform_id)
        data_stream.writeQString(deform_name)

    return payload

def decodeDeformPayload(payload):
    data_stream = QDataStream(payload, QIODevice.ReadOnly)

    deform_entries = []
    for _ in range(data_stream.readInt32()):
        deform_id = data_stream.readInt64()
        deform_name = data_stream.readQString()
        deform_entries.append((deform_id, deform_name))

    return deform_entries

class SkinningEditorDeformList(QListWidget):
    def __init__(self, deformer_dict = {}, parent=None):
        super().__init__(parent)
        self.tab = parent
        self.deformer_dict = deformer_dict
        #{node_id: {"label", "deforms": [{"id", "name", "status"}, ...]}} - unlike
        #deformer_dict, this persists across updates so a deform that disappeared
        #from the node graph keeps showing here (status=removed) until explicitly
        #cleared via the "Remove Deprecated" button, rather than vanishing silently
        self.tracked_dict = {}
        self.initUI()

    def initUI(self):
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setMaximumWidth(250)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)

        for key, group in self.tracked_dict.items():
            group_entries = getGroupEntries(group)

            base_item = QListWidgetItem(self)
            list_group_item = List_Group_Item(getGroupLabel(key, group), group_entries, self)
            #dragging the group header drags everything under it
            list_group_item.setDragCallback(self.startGroupDrag)
            list_group_item.adjustSize()
            base_item.setSizeHint(list_group_item.sizeHint())
            base_item.setBackground(QColor(50, 50, 50))

            self.setItemWidget(base_item, list_group_item)
            base_item.setFlags(base_item.flags() & ~Qt.ItemIsSelectable)

            for entry in group_entries:
                item = self.addDragListItem(entry["name"], entry["id"], entry["status"], "")
                list_group_item.addListItem(item)

    def addDragListItem(self, name, deform_id, status = STATUS_NORMAL, icon=None):
        item = QListWidgetItem(name, self)

        icon_str = icon if icon is not None else ""
        icon_path = os.path.join(ICONPATH, icon_str)
        icon_pixmap = QPixmap(icon_path if icon_str != "" else os.path.join(ICONPATH, "default_node.png"))
        item.setIcon(QIcon(icon_pixmap))
        item.setSizeHint(QSize(32,32))

        item.setData(DEFORM_ID_ROLE, deform_id)
        item.setData(DEFORM_STATUS_ROLE, status)

        if status == STATUS_REMOVED:
            item.setBackground(REMOVED_COLOR)
            #no longer exists in the graph - nothing to resolve on the other end
            #of a drop, so don't offer it as draggable. The flag has to be cleared
            #explicitly: QListWidgetItem is drag-enabled by default, so only
            #*adding* it for the other statuses left these draggable too
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)
        elif status == STATUS_ADDED:
            item.setBackground(ADDED_COLOR)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled)
        else:
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled)

        return item

    def isItemDraggable(self, item):
        return item.data(DEFORM_STATUS_ROLE) != STATUS_REMOVED

    def startDrag(self, *args, **kwargs):
        if DRAGDROP_DEBUG: print("SKINNINGDEFORMLIST:: --startDrag:: ")

        #the whole selection, not just the row under the cursor - the list has
        #always run in ExtendedSelection, only the payload was single-item
        draggable_items = [item for item in self.selectedItems() if self.isItemDraggable(item)]

        if draggable_items == []:
            current_item = self.currentItem()
            if current_item is not None and self.isItemDraggable(current_item):
                draggable_items = [current_item]

        self.startDragForItems(draggable_items)

    def startGroupDrag(self, list_group_item):
        #dragging a group header behaves as if every deform under it had been
        #selected and dragged
        if DRAGDROP_DEBUG: print("SKINNINGDEFORMLIST:: --startGroupDrag:: ", list_group_item.name)

        draggable_items = [item for item in list_group_item.list_items if self.isItemDraggable(item)]
        self.startDragForItems(draggable_items)

    def startDragForItems(self, items):
        if items == []:
            if DRAGDROP_DEBUG: print("SKINNINGDEFORMLIST:: --startDragForItems:: nothing draggable in this drag")
            return

        try:
            deform_entries = [(item.data(DEFORM_ID_ROLE), item.text()) for item in items]

            mime_data = QMimeData()
            mime_data.setData(SKINDEFORM_MIMETYPE, encodeDeformPayload(deform_entries))

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(QPoint(0, 0))

            drag.exec_(Qt.MoveAction)

        except Exception as e:
            print("SKINNINGDEFORMLIST:: --startDragForItems:: ", e)

    def rebuildRows(self):
        #every refresh rebuilds the whole list, which sends the scrollbar back to
        #the top. Dropping a deform onto a component triggers one of these, so
        #working down a long list meant scrolling back down after every drop.
        #updateGeometries() recomputes the scrollbar range for the rows just added
        #- without it the restore clamps against the pre-rebuild range
        scroll_position = self.verticalScrollBar().value()

        self.clear()
        self.initUI()

        self.updateGeometries()
        self.verticalScrollBar().setValue(scroll_position)

    def updateDeformerList(self, deformer_dict):
        self.deformer_dict = deformer_dict
        self.tracked_dict = self.mergeTrackedState(self.tracked_dict, deformer_dict)
        self.rebuildRows()
        self.tab.updateRemoveDeprecatedButtonState()
        self.tab.updateAcceptNewButtonState()

    def findOldGroupKeyByLabel(self, old_tracked, label):
        #groups used to be keyed by the component prefix and are now keyed by node
        #id, so a project saved before that change has to be paired up by label -
        #otherwise the first refresh after upgrading reports every deform as
        #removed and re-added
        for old_key, old_group in old_tracked.items():
            if getGroupLabel(old_key, old_group) == label:
                return old_key
        return None

    def mergeTrackedState(self, old_tracked, new_dict):
        merged = {}
        unmatched_old_keys = set(old_tracked.keys())

        for key, group in new_dict.items():
            label = getGroupLabel(key, group)

            old_key = key if key in old_tracked else self.findOldGroupKeyByLabel(old_tracked, label)
            if old_key is not None:
                unmatched_old_keys.discard(old_key)

            merged_entries = self.mergeGroupEntries(getGroupEntries(old_tracked.get(old_key, [])),
                                                    getGroupEntries(group))
            if merged_entries:
                merged[key] = {"label": label, "deforms": merged_entries}

        #a group with no counterpart in the current graph at all - its component
        #was deleted, so everything under it is genuinely gone
        for old_key in unmatched_old_keys:
            old_group = old_tracked[old_key]
            removed_entries = [{"id": entry["id"], "name": entry["name"], "status": STATUS_REMOVED}
                               for entry in getGroupEntries(old_group)]
            if removed_entries:
                merged[old_key] = {"label": getGroupLabel(old_key, old_group), "deforms": removed_entries}

        return merged

    def mergeGroupEntries(self, old_entries, new_entries):
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

        return merged_entries

    def getAllTrackedEntries(self):
        return [entry for group in self.tracked_dict.values() for entry in getGroupEntries(group)]

    def hasDeprecatedEntries(self):
        return any(entry["status"] == STATUS_REMOVED for entry in self.getAllTrackedEntries())

    def hasNewEntries(self):
        return any(entry["status"] == STATUS_ADDED for entry in self.getAllTrackedEntries())

    def clearDeprecatedEntries(self):
        cleaned = {}
        for key, group in self.tracked_dict.items():
            remaining = [entry for entry in getGroupEntries(group) if entry["status"] != STATUS_REMOVED]
            if remaining:
                cleaned[key] = {"label": getGroupLabel(key, group), "deforms": remaining}
        self.tracked_dict = cleaned
        self.rebuildRows()

    def acceptNewEntries(self):
        for entry in self.getAllTrackedEntries():
            if entry["status"] == STATUS_ADDED:
                entry["status"] = STATUS_NORMAL
        self.rebuildRows()
