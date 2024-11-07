from PySide2 import QtWidgets

class NodeEditor_QGraphicView(QtWidgets.QGraphicsView):
    def __init__(self, grScene, parent=None):
        super().__init__(parent)

        self.grScene = grScene
        
        self.setScene = self.grScene

        self.initUI()


    def initUI(self):
        pass