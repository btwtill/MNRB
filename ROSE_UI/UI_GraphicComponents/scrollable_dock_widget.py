from PySide6.QtWidgets import QDockWidget, QScrollArea, QFrame #type: ignore

class ScrollableDockWidget(QDockWidget):
    """A dock whose contents scroll once they outgrow it.

    Drop-in for QDockWidget: setWidget() puts the widget inside an internal
    QScrollArea instead of directly into the dock, so callers don't have to know
    the scroll area exists. The properties panels grow with the number of fields
    on a node, and without this everything past the dock's height was unreachable.
    """

    def __init__(self, title, parent = None):
        super().__init__(title, parent)

        self.scroll_area = QScrollArea(self)
        #the panel fills the dock's width and only grows vertically - without this
        #it keeps its size hint and sits in the top-left corner of the viewport
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        super().setWidget(self.scroll_area)

    def setWidget(self, widget):
        #takeWidget() rather than letting setWidget() replace it: QScrollArea
        #*deletes* the widget it currently holds when a new one is set, and these
        #panels are owned by their node (node.properties) and shown again later
        self.scroll_area.takeWidget()
        self.scroll_area.setWidget(widget)

    def widget(self):
        return self.scroll_area.widget()
