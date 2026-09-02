from PySide6.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView, QSizePolicy #type: ignore
from PySide6.QtCore import Qt, QDataStream, QIODevice #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_ClusterComponentWidget import SkinClusterComponentWidget #type: ignore
from MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_DeformList import SKINDEFORM_MIMETYPE #type: ignore

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
        self.clear()
        for skin_cluster in self.tab.skin_clusters:
            self.addSkinClusterItem(skin_cluster)
        self.tab.updateRemoveDeprecatedButtonState()

    def addSkinClusterItem(self, skin_cluster):
        base_item = QListWidgetItem(self)
        component_widget = SkinClusterComponentWidget(skin_cluster, self.tab, self)
        component_widget.adjustSize()
        base_item.setSizeHint(component_widget.sizeHint())

        self.addItem(base_item)
        self.setItemWidget(base_item, component_widget)

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
        event_data = event.mimeData().data(SKINDEFORM_MIMETYPE)

        data_stream = QDataStream(event_data, QIODevice.ReadOnly)
        deform_id = data_stream.readInt64()
        deform_name = data_stream.readQString()

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
        deform = scene.getDeformById(deform_id)
        if deform is None:
            deform = scene.getDeformByName(deform_name)

        if deform is None:
            if DRAGDROP_DEBUG: print("SKINNINGCLUSTERLIST:: --handleDeformDrop:: Could not resolve dropped deform:: ", deform_name)
            event.ignore()
            return

        component_widget.skin_cluster.addDeform(deform)
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
