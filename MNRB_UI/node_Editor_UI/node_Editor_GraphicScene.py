from PySide2 import QtWidgets

class NodeEditor_GraphicScene(QtWidgets.QGraphicsScene):
    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.scene = scene