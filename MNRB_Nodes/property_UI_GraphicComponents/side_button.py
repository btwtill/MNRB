from PySide2.QtWidgets import QPushButton #type: ignore

class MirroringSidePrefixButton(QPushButton):
    def __init__(self, properties_widget, text = "", value = "M_", marked = False, parent = None):
        super().__init__(text, parent)
        self.name = text
        self.value = value

        self.is_marked = marked
        self.propertie_widget = properties_widget

        self.buttons_to_deselect = []

        if self.is_marked:
            self.mark()

    def mark(self):
        self.is_marked = True
        self.propertie_widget.component_side_prefix = self.value
        
        self.setStyleSheet("background-color: #FF336600;")

        for button in self.buttons_to_deselect:
            button.markDeselected()

    def markDeselected(self):
        self.is_marked = False
        self.setStyleSheet("")

    def addButtonForDeselection(self, button):
        self.buttons_to_deselect.append(button)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.mark()

        
        