from PySide2.QtWidgets import QPushButton #type: ignore

class MirroringSidePrefixButton(QPushButton):
    def __init__(self, text = "", parent = None):
        super().__init__(text, parent)
        self.name = text
        self.is_marked = False

        self.buttons_to_deselect = []

    def markSelected(self):
        self.is_marked = True
        self.setStyleSheet("background-color: #FF336600;")

    def markDeselected(self):
        self.is_marked = False
        self.setStyleSheet("")

    def addButtonForDeselection(self, button):
        self.buttons_to_deselect.append(button)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        self.markSelected()

        for button in self.buttons_to_deselect:
            button.markDeselected()
        