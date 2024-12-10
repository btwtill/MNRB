from PySide2.QtWidgets import QWidget, QVBoxLayout, QFrame #type: ignore


class SeparatorWidget(QFrame):
    def __init__(self, height = 5, parent = None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        
