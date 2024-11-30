from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel #type: ignore

class MNRBPreferences(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("MNRB Preferences")
        self.setGeometry(150, 150, 200, 200)

        self.layout = QVBoxLayout()
        self.preference_label = QLabel("This will be the preferences!!")
        self.layout.addWidget(self.preference_label)

        self.setLayout(self.layout)