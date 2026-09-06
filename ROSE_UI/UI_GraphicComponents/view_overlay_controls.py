from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton #type: ignore
from PySide6.QtCore import Qt #type: ignore

BUTTON_SIZE = 24
#one press of a pan button, in view pixels
PAN_STEP = 90
#gap between the cluster and the view's bottom-right corner
VIEW_MARGIN = 12

OVERLAY_STYLE = """
QWidget#viewOverlayControls {
    background-color: #B4232323;
    border: 1px solid #FF555555;
    border-radius: 4px;
}
QPushButton {
    background-color: #FF3D3D3D;
    border: 1px solid #FF555555;
    border-radius: 3px;
    color: #FFDDDDDD;
}
QPushButton:hover { background-color: #FF4D4D4D; }
QPushButton:pressed { background-color: #FFFFA637; color: #FF222222; }
"""

class ViewOverlayControls(QWidget):
    """Zoom and pan buttons floating over a graphics view, for driving the canvas
    without a mouse wheel or a middle mouse button.

    A plain child of the view rather than something in a layout - the view has no
    layout of its own - so it positions itself against the view's corner in
    reposition(), which the view calls on resize.
    """

    def __init__(self, view):
        super().__init__(view)

        self.view = view
        self.initUI()

    def initUI(self):
        self.setObjectName("viewOverlayControls")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(OVERLAY_STYLE)

        layout = QGridLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        layout.addWidget(self.buildButton("▲", "Pan up", lambda: self.view.panBy(0, -PAN_STEP)), 0, 1)
        layout.addWidget(self.buildButton("◀", "Pan left", lambda: self.view.panBy(-PAN_STEP, 0)), 1, 0)
        layout.addWidget(self.buildButton("☉", "Frame all nodes", self.view.centerView), 1, 1)
        layout.addWidget(self.buildButton("▶", "Pan right", lambda: self.view.panBy(PAN_STEP, 0)), 1, 2)
        layout.addWidget(self.buildButton("▼", "Pan down", lambda: self.view.panBy(0, PAN_STEP)), 2, 1)

        layout.addWidget(self.buildButton("−", "Zoom out", self.view.zoomOut), 3, 0)
        layout.addWidget(self.buildButton("+", "Zoom in", self.view.zoomIn), 3, 2)

    def buildButton(self, label, tooltip, on_clicked):
        button = QPushButton(label)
        button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        button.setToolTip(tooltip)
        #the canvas takes focus back after a press, so the space bar and the
        #editor's own shortcuts don't start re-triggering whichever button was
        #clicked last
        button.setFocusPolicy(Qt.NoFocus)
        button.clicked.connect(on_clicked)
        return button

    def reposition(self):
        self.adjustSize()
        self.move(self.view.width() - self.width() - VIEW_MARGIN,
                  self.view.height() - self.height() - VIEW_MARGIN)
