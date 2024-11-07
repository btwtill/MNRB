from PySide2 import QtWidgets, QtCore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_Widget import NodeEditorWidget

class mnrb_NodeEditorTab(QtWidgets.QMainWindow):
    def __init__(self, ):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Central widget for secondary main window

        central_widget = NodeEditorWidget()

        # Set the central widget for the secondary main window
        self.setCentralWidget(central_widget)

        # Add dock widgets to the secondary main window
        self.add_dock_widgets()

    def add_dock_widgets(self):
        """Add left and right dock widgets to the secondary main window."""

        # Left dock widget
        left_dock = QtWidgets.QDockWidget("Left Dock", self)
        left_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        left_dock_contents = QtWidgets.QWidget()
        left_dock_layout = QtWidgets.QVBoxLayout(left_dock_contents)
        left_dock_label = QtWidgets.QLabel("This is the left dock widget.")
        left_dock_layout.addWidget(left_dock_label)
        left_dock_contents.setLayout(left_dock_layout)
        left_dock.setWidget(left_dock_contents)

        # Add the left dock widget to the secondary main window
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, left_dock)

        # Right dock widget
        right_dock = QtWidgets.QDockWidget("Right Dock", self)
        right_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        right_dock_contents = QtWidgets.QWidget()
        right_dock_layout = QtWidgets.QVBoxLayout(right_dock_contents)
        right_dock_label = QtWidgets.QLabel("This is the right dock widget.")
        right_dock_layout.addWidget(right_dock_label)
        right_dock_contents.setLayout(right_dock_layout)
        right_dock.setWidget(right_dock_contents)
        
        # Add the right dock widget to the secondary main window
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, right_dock)


