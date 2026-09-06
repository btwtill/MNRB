import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication #type: ignore
from PySide6.QtGui import QColor, QIcon #type: ignore
from PySide6.QtCore import Qt #type: ignore
from MNRB.ROSE_UI.UI_GraphicComponents.triangleWidget import TriangleWidget #type: ignore

class List_Group_Item(QWidget):
    def __init__(self, name, item_ids, parent = None):
        super().__init__(parent)

        self.item_ids = item_ids
        self.name = name
        self.list_items = []

        #optional - set by an owner that wants dragging the header to mean
        #"drag everything in this group" (see SkinningEditorDeformList). Without
        #one the header is click-to-collapse only, as before.
        self.drag_callback = None
        self._press_position = None

        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout(self)

        self.layout.setContentsMargins(10,10,10,10)  # Add some padding
        self.layout.setSpacing(10)

        self.triangle_widget = TriangleWidget(self)
        self.triangle_widget.setFixedSize(20, 20)
        self.triangle_widget.setColor(QColor("#FF181818"))
        self.title = QLabel(self.name)

        self.layout.addWidget(self.triangle_widget)
        self.layout.addWidget(self.title)

        self.setLayout(self.layout)

        self.triangle_widget.rotate()

    def addListItem(self, item):
        self.list_items.append(item)

    def setDragCallback(self, callback):
        self.drag_callback = callback

    def toggleCollapsed(self):
        for node_list_item in self.list_items:
            node_list_item.setHidden(not node_list_item.isHidden())
        self.triangle_widget.rotate()
        self.triangle_widget.update()

    def mousePressEvent(self, event):
        #collapsing now happens on release rather than press, so that dragging the
        #header doesn't also collapse the group on the way out
        self._press_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        has_pending_press = self._press_position is not None and self.drag_callback is not None
        if not has_pending_press or not (event.buttons() & Qt.LeftButton):
            return super().mouseMoveEvent(event)

        moved = (event.position().toPoint() - self._press_position).manhattanLength()
        if moved < QApplication.startDragDistance():
            return super().mouseMoveEvent(event)

        #cleared first: this press turned into a drag, so the release that ends it
        #must not be read as a collapse click
        self._press_position = None
        self.drag_callback(self)

    def mouseReleaseEvent(self, event):
        if self._press_position is not None:
            self._press_position = None
            self.toggleCollapsed()
        super().mouseReleaseEvent(event)
