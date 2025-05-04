from PySide2.QtWidgets import QListWidget #type: ignore

class SkinningEditorDeformList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tab = parent

        self.initUI()

    def initUI(self):
        deformer_list = self.tab.getComponentDeformerList()