from PySide6.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView, QSizePolicy #type: ignore
from PySide6.QtCore import Qt #type: ignore
from MNRB.ROSE_UI.skinning_Editor_UI.skinning_Editor_ClusterComponentWidget import SkinClusterComponentWidget #type: ignore
from MNRB.ROSE_UI.skinning_Editor_UI.skinning_Editor_DeformList import SKINDEFORM_MIMETYPE, decodeDeformPayload #type: ignore

DRAGDROP_DEBUG = False

class SkinningEditorClusterList(QListWidget):
    def __init__(self, tab, parent=None):
        super().__init__(parent)

        self.tab = tab

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setAcceptDrops(True)
        self.setSpacing(4)
        #default ScrollPerItem jumps a whole box height per wheel step - pixel-based
        #scrolling reads as smooth instead of snapping between boxes
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.rebuild()

    def rebuild(self):
        #this runs on every deform drop (handleDeformDrop), and clear() + re-add
        #sends the scrollbar back to the top - which meant scrolling back down to
        #the box being filled after every single drop. updateGeometries() gets the
        #scrollbar range recomputed for the rows just added, so the restore below
        #isn't clamped against the pre-rebuild range.
        scroll_position = self.verticalScrollBar().value()

        self.clear()
        for skin_cluster in self.tab.skin_clusters:
            self.addSkinClusterItem(skin_cluster)

        self.updateGeometries()
        self.verticalScrollBar().setValue(scroll_position)

        self.tab.updateRemoveDeprecatedButtonState()

    def getComponentWidgetSizeHint(self, component_widget):
        component_widget.adjustSize()
        size_hint = component_widget.sizeHint()
        #a box with its deform list collapsed can hint shorter than its own
        #minimum height, which would clip it inside the row
        size_hint.setHeight(max(size_hint.height(), component_widget.minimumHeight()))
        return size_hint

    def addSkinClusterItem(self, skin_cluster):
        base_item = QListWidgetItem(self)
        component_widget = SkinClusterComponentWidget(skin_cluster, self.tab, self)
        base_item.setSizeHint(self.getComponentWidgetSizeHint(component_widget))

        self.addItem(base_item)
        self.setItemWidget(base_item, component_widget)

    def updateItemSizeForWidget(self, component_widget):
        #re-hint just this box's row. Used where a box changes height from inside
        #one of its own signal handlers, which rules out rebuild() - that deletes
        #the very widget whose handler is still running.
        for index in range(self.count()):
            item = self.item(index)
            if self.itemWidget(item) is component_widget:
                item.setSizeHint(self.getComponentWidgetSizeHint(component_widget))
                return

    def refreshAll(self):
        for index in range(self.count()):
            widget = self.itemWidget(self.item(index))
            if widget is not None:
                widget.refresh()
        self.tab.updateRemoveDeprecatedButtonState()

    def mousePressEvent(self, event):
        #a click that doesn't land on any box's widget is a click on empty space
        #within the list - clears the current selection, matching standard list UX
        if self.itemAt(event.pos()) is None:
            self.tab.deselectAllSkinClusters()
            self.refreshAll()
            self.tab.notifySelectionChanged()
        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(SKINDEFORM_MIMETYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(SKINDEFORM_MIMETYPE):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasFormat(SKINDEFORM_MIMETYPE):
            self.handleDeformDrop(event)
            return

        #not our custom drop - let Qt handle the internal reorder drag natively
        super().dropEvent(event)
        self.syncClusterOrderFromWidgetOrder()

    def handleDeformDrop(self, event):
        #one drop can carry many deforms now - a multi selection, or a whole group
        #dragged by its header
        deform_entries = decodeDeformPayload(event.mimeData().data(SKINDEFORM_MIMETYPE))

        target_item = self.itemAt(event.pos())
        if target_item is None:
            if DRAGDROP_DEBUG: print("SKINNINGCLUSTERLIST:: --handleDeformDrop:: No cluster box under drop position")
            event.ignore()
            return

        component_widget = self.itemWidget(target_item)
        if component_widget is None:
            event.ignore()
            return

        scene = self.tab.getScene()
        added_count = 0

        for deform_id, deform_name in deform_entries:
            deform = scene.getDeformById(deform_id)
            if deform is None:
                deform = scene.getDeformByName(deform_name)

            if deform is None:
                if DRAGDROP_DEBUG: print("SKINNINGCLUSTERLIST:: --handleDeformDrop:: Could not resolve dropped deform:: ", deform_name)
                continue

            #addDeform ignores one already in this container, so overlapping
            #selections and group drags don't duplicate rows
            component_widget.skin_cluster.addDeform(deform)
            added_count += 1

        if added_count == 0:
            event.ignore()
            return

        self.tab.setModified(True)
        #deform count changed -> box size changed -> needs a fresh size hint,
        #same reasoning as onRemoveDeform in the component widget
        self.rebuild()

        event.setDropAction(Qt.CopyAction)
        event.accept()

    def syncClusterOrderFromWidgetOrder(self):
        new_order = []
        for index in range(self.count()):
            widget = self.itemWidget(self.item(index))
            if widget is not None:
                new_order.append(widget.skin_cluster)
        if new_order != self.tab.skin_clusters:
            self.tab.setModified(True)
        self.tab.skin_clusters = new_order
