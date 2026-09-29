import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QApplication #type: ignore
from PySide6.QtGui import QColor, QIcon #type: ignore
from PySide6.QtCore import Qt #type: ignore
from MNRB.ROSE_UI.UI_GraphicComponents.triangleWidget import TriangleWidget #type: ignore

#the arrow, light enough to read on the header's grey
ARROW_COLOR = QColor("#FFAAAAAA")


class ExpandableGroupsMixin:
    """For a list built from List_Group_Items: remembers which groups the user
    opened, by name, so a rebuild - these lists rebuild whenever the graph
    changes - does not snap everything shut again. Groups start closed."""

    def getExpandedGroups(self):
        if not hasattr(self, "_expanded_groups"):
            self._expanded_groups = set()
        return self._expanded_groups

    def isGroupExpanded(self, name):
        return name in self.getExpandedGroups()

    def onGroupExpansionChanged(self, group_item, is_expanded):
        if is_expanded:
            self.getExpandedGroups().add(group_item.name)
        else:
            self.getExpandedGroups().discard(group_item.name)

    def createGroupItem(self, name, item_ids):
        group_item = List_Group_Item(name, item_ids, self, expanded = self.isGroupExpanded(name))
        group_item.setExpansionListener(self.onGroupExpansionChanged)
        return group_item


class List_Group_Item(QWidget):
    def __init__(self, name, item_ids, parent = None, expanded = False):
        super().__init__(parent)

        self.item_ids = item_ids
        self.name = name
        self.list_items = []

        #closed by default: a tab opening on every group spelled out is a wall of
        #rows, and the headers alone are the overview
        self.is_expanded = expanded
        self.expansion_listener = None

        #optional - set by an owner that wants dragging the header to mean
        #"drag everything in this group" (see SkinningEditorDeformList). Without
        #one the header is click-to-collapse only, as before.
        self.drag_callback = None
        self._press_position = None

        self.initUI()

    def initUI(self):
        #styled by rose_style's #listGroupHeader rule - rounded, with a hover
        self.setObjectName("listGroupHeader")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(Qt.PointingHandCursor)

        self.layout = QHBoxLayout(self)

        self.layout.setContentsMargins(8, 6, 8, 6)
        self.layout.setSpacing(8)

        self.triangle_widget = TriangleWidget(self)
        self.triangle_widget.setFixedSize(14, 14)
        self.triangle_widget.setColor(ARROW_COLOR)
        self.title = QLabel(self.name)
        self.title.setStyleSheet("font-weight: bold; background: transparent;")

        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #888888; background: transparent;")

        self.layout.addWidget(self.triangle_widget)
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.count_label)

        self.setLayout(self.layout)

        self.triangle_widget.is_rotated = self.is_expanded

    def addListItem(self, item):
        self.list_items.append(item)
        item.setHidden(not self.is_expanded)
        #a closed group still says how much is in it
        self.count_label.setText(str(len(self.list_items)))

    def setExpansionListener(self, callback):
        self.expansion_listener = callback

    def setExpanded(self, is_expanded):
        self.is_expanded = is_expanded
        for list_item in self.list_items:
            list_item.setHidden(not is_expanded)
        self.triangle_widget.is_rotated = is_expanded
        self.triangle_widget.update()

        if self.expansion_listener is not None:
            self.expansion_listener(self, is_expanded)

    def setDragCallback(self, callback):
        self.drag_callback = callback

    def toggleCollapsed(self):
        self.setExpanded(not self.is_expanded)

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
