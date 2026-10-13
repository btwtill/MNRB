from PySide6.QtWidgets import QPlainTextEdit, QSizePolicy, QFrame #type: ignore
from PySide6.QtCore import Qt, Signal #type: ignore
from PySide6.QtGui import QTextOption #type: ignore

#a break opportunity that draws nothing - wrapping can happen there
ZERO_WIDTH_SPACE = "​"


def softBreaks(text):
    """The text with places to wrap after . : _ | and /, so a long plug or node
    name wraps in a word-wrapped label instead of forcing the panel wider."""
    for character in ".:_|/":
        text = text.replace(character, character + ZERO_WIDTH_SPACE)
    return text


class WrappingLineEdit(QPlainTextEdit):
    """A one-value text field that wraps onto as many lines as its text needs.

    A QLineEdit in a narrow panel hides everything past its width; this shows
    all of it. It reads like a QLineEdit to the code using it - text(),
    setText(), editingFinished on Enter or leaving the field - and Enter
    commits rather than adding a line, the value being one line of text.
    """

    editingFinished = Signal()

    def __init__(self, text = "", parent = None, max_lines = 8):
        super().__init__(parent)
        self.max_lines = max_lines
        self.setTabChangesFocus(True)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        #anywhere, not only at spaces - a plug name has none
        self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setFrameShape(QFrame.StyledPanel)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.document().setDocumentMargin(2)
        self.textChanged.connect(self.fitHeight)
        #the whole value on hover too, past the line limit
        self.textChanged.connect(lambda: self.setToolTip(self.toPlainText()))
        self.setText(text)

    def text(self):
        return self.toPlainText()

    def setText(self, text):
        if text != self.toPlainText():
            self.setPlainText(text)
        self.fitHeight()

    def lineCount(self):
        lines = 0
        block = self.document().begin()
        while block.isValid():
            layout = block.layout()
            lines += max(layout.lineCount() if layout is not None else 1, 1)
            block = block.next()
        return max(lines, 1)

    def fitHeight(self):
        lines = min(self.lineCount(), self.max_lines)
        line_height = self.fontMetrics().lineSpacing()
        margins = self.contentsMargins()
        frame = margins.top() + margins.bottom() + 2 * int(self.document().documentMargin()) + 2
        self.setFixedHeight(lines * line_height + frame)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        #a new width wraps the text onto a different number of lines
        self.fitHeight()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.editingFinished.emit()
            return
        super().keyPressEvent(event)

    def insertFromMimeData(self, source):
        #pasted text stays one value - line breaks become spaces
        if source.hasText():
            self.insertPlainText(" ".join(source.text().splitlines()))
            return
        super().insertFromMimeData(source)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.editingFinished.emit()
