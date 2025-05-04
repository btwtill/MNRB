from PySide2.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QHBoxLayout, QSizePolicy #type: ignore
from PySide2.QtCore import Qt #type: ignore
from MNRB.MNRB_UI.UI_GraphicComponents.triangleWidget import TriangleWidget #type: ignore

class IconWidgetBar(QWidget):
    def __init__(self, receit_widget, text = "Undefined", height=20, parent=None):
        super(IconWidgetBar, self).__init__(parent)

        self.receit_widget = receit_widget

        # Set fixed height for the widget
        self.setFixedHeight(height)

        # Apply darker background using QSS
        #self.setStyleSheet("background-color: #2B2B2B;")

        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)  # Add some padding
        self.layout.setSpacing(10)

        self.triangle_widget = TriangleWidget(self)
        self.triangle_widget.setFixedSize(height, height)

        # Spacer to stretch width
        self.spacer = QLabel(self)
        self.spacer.setText(text)
        self.spacer.setAlignment(Qt.AlignCenter)
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # Stretch width

        # Add icon and spacer to layout
        self.layout.addWidget(self.triangle_widget)
        self.layout.addWidget(self.spacer)

        # Set the layout
        self.setLayout(self.layout)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.triangle_widget.rotate()
        self.receit_widget.toggle_content()


class ReceitWidget(QWidget):
    def __init__(self, title="Expandable Widget", parent=None):
        super(ReceitWidget, self).__init__(parent)
        
        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        #set style
        #self.setStyleSheet("background-color: #2B2B2B;")

        # Toggle Button
        self.base_area_widget = IconWidgetBar(self, title)
        
        # Content Area
        self.content_area = QFrame()
        self.content_layout = QVBoxLayout(self.content_area)
        self.contet_visibility = False
        self.content_area.setVisible(self.contet_visibility)  # Start collapsed

        # Add button and content to the layout
        self.main_layout.addWidget(self.base_area_widget)
        self.main_layout.addWidget(self.content_area)

    def toggle_content(self):
        self.contet_visibility = not self.contet_visibility
        self.content_area.setVisible(self.contet_visibility)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        self.content_layout.addLayout(layout)
