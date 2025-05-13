from PySide2.QtWidgets import QListWidget, QSizePolicy #type: ignore

class SkinningEditorDeformList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tab = parent

        self.initUI()

    def initUI(self):
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setMaximumWidth(350)
        deformer_list = self.tab.getComponentDeformerDict()