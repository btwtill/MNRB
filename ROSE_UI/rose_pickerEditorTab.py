from collections import OrderedDict
import copy
import json
import os

from PySide6 import QtCore, QtGui, QtWidgets #type: ignore

from MNRB.ROSE_Data.rose_Editor_Serializable import Serializable #type: ignore
from MNRB.ROSE_UI.rose_ui_utils import findProjectGraphFile #type: ignore
from MNRB.ROSE_UI.picker_Editor_UI import picker_document as document_model #type: ignore
from MNRB.ROSE_UI.picker_Editor_UI import picker_runtime as runtime #type: ignore
from MNRB.ROSE_UI.picker_Editor_UI import picker_svg #type: ignore
from MNRB.ROSE_UI.picker_Editor_UI.picker_canvas import (PickerCanvas, PickerView, TOOL_SELECT, TOOL_RECT, #type: ignore
                                                         TOOL_ELLIPSE, TOOL_POLYGON, TOOL_TEXT)
from MNRB.ROSE_naming.ROSE_names import ROSE_Names #type: ignore
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.picker")

#how many undo steps are kept
HISTORY_LIMIT = 100
#property edits settle into one undo step after this long without another change
COMMIT_DELAY_MS = 400

ACTION_LABELS = [("none", "Nothing (decoration or label)"), ("select", "Select Controls"),
                 ("builtin", "Ready-made Action"), ("code", "Run Code")]
CONTROL_ID_ROLE = QtCore.Qt.ItemDataRole.UserRole


class ColorButton(QtWidgets.QPushButton):
    """A swatch that opens a colour picker; emits colorChanged with a #RRGGBB string."""

    colorChanged = QtCore.Signal(str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.color = "#FFFFFF"
        self.setFixedWidth(48)
        self.clicked.connect(self.pick)

    def setColor(self, color):
        self.color = color
        self.setStyleSheet("QPushButton { background-color: %s; }" % color)

    def pick(self):
        chosen = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.color), self, "Colour")
        if chosen.isValid():
            self.setColor(chosen.name())
            self.colorChanged.emit(self.color)


class PythonHighlighter(QtGui.QSyntaxHighlighter):
    """Just enough colour to read button code: keywords, strings, comments."""

    KEYWORDS = ("and as assert break class continue def del elif else except False finally for from global if "
                "import in is lambda None not or pass raise return True try while with yield").split()

    def __init__(self, document):
        super().__init__(document)
        def style(color, bold = False):
            text_format = QtGui.QTextCharFormat()
            text_format.setForeground(QtGui.QColor(color))
            if bold:
                text_format.setFontWeight(QtGui.QFont.Bold)
            return text_format
        self.rules = [(QtCore.QRegularExpression(r"\b(%s)\b" % "|".join(self.KEYWORDS)), style("#CC7832", True)),
                      (QtCore.QRegularExpression(r"\b(rig|cmds|mel)\b"), style("#9876AA")),
                      (QtCore.QRegularExpression(r"\"[^\"\n]*\"|'[^'\n]*'"), style("#6A8759")),
                      (QtCore.QRegularExpression(r"#[^\n]*"), style("#808080"))]

    def highlightBlock(self, text):
        for expression, text_format in self.rules:
            matches = expression.globalMatch(text)
            while matches.hasNext():
                match = matches.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), text_format)


class rose_PickerEditorTab(QtWidgets.QMainWindow, Serializable):
    """Draw the animator's rig picker: shapes on a fixed-size page, each one
    doing one thing when clicked - selecting controls, running a ready-made
    action, or running its own code.

    The Picker pipeline step writes it out as a self-contained script next to
    the exported rig (see picker_document.writePickerScript)."""

    def __init__(self, node_editor, parent = None):
        QtWidgets.QMainWindow.__init__(self, parent)
        Serializable.__init__(self)

        self.is_tab_widget = True
        self.node_editor = node_editor
        self.document = document_model.newDocument()
        self.failed_load_path = None

        self.history = []
        self.history_index = -1
        self.updating_panel = False

        self._has_been_modified = False
        self._has_been_modified_listeners = []
        self._selection_changed_listeners = []

        self.commit_timer = QtCore.QTimer(self)
        self.commit_timer.setSingleShot(True)
        self.commit_timer.timeout.connect(lambda: self.commit("Edit properties"))

        self.initUI()
        self.resetHistory()

    def getScene(self):
        return self.node_editor.central_widget.scene

# UI

    def initUI(self):
        self.canvas = PickerCanvas(self)
        self.view = PickerView(self.canvas, self)
        self.canvas.selectionChanged.connect(self.onSelectionChanged)

        self.addToolBar(self.buildToolbar())

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.view)
        panel_scroll = QtWidgets.QScrollArea()
        panel_scroll.setWidgetResizable(True)
        panel_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        panel_scroll.setWidget(self.buildPropertiesPanel())
        panel_scroll.setMinimumWidth(360)
        splitter.addWidget(panel_scroll)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        self.canvas.rebuild()
        QtCore.QTimer.singleShot(0, self.view.frame)

    def buildToolbar(self):
        toolbar = QtWidgets.QToolBar("Picker")
        toolbar.setMovable(False)
        self.tool_actions = {}
        group = QtGui.QActionGroup(self)
        for tool, label, tip in ((TOOL_SELECT, "Select", "Select, move and resize shapes (Esc)"),
                                 (TOOL_RECT, "Rectangle", "Drag to draw a rectangle"),
                                 (TOOL_ELLIPSE, "Ellipse", "Drag to draw an ellipse"),
                                 (TOOL_POLYGON, "Polygon", "Click the corners; double-click or Enter to finish"),
                                 (TOOL_TEXT, "Text", "Drag or click to place a text label")):
            action = toolbar.addAction(label, lambda tool = tool: self.view.setTool(tool))
            action.setCheckable(True)
            action.setToolTip(tip)
            group.addAction(action)
            self.tool_actions[tool] = action
        self.tool_actions[TOOL_SELECT].setChecked(True)

        toolbar.addSeparator()
        import_action = toolbar.addAction("Import SVG...", self.onImportSvg)
        import_action.setToolTip("Turn the drawing in an SVG file into picker shapes - fitted onto the page "
                                 "if it is larger")
        toolbar.addSeparator()
        self.duplicate_action = toolbar.addAction("Duplicate", self.onDuplicate)
        self.delete_action = toolbar.addAction("Delete", self.onDelete)
        toolbar.addSeparator()
        self.forward_action = toolbar.addAction("Bring Forward", lambda: self.onReorder(1))
        self.backward_action = toolbar.addAction("Send Backward", lambda: self.onReorder(-1))
        toolbar.addSeparator()
        self.snap_action = toolbar.addAction("Snap", self.onToggleSnap)
        self.snap_action.setCheckable(True)
        self.snap_action.setChecked(True)
        self.snap_action.setToolTip("Snap to a %g pixel grid" % 5)
        toolbar.addAction("Frame Page", self.view.frame)
        return toolbar

    def buildPropertiesPanel(self):
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)

        #the page - always there
        page_box = QtWidgets.QGroupBox("Page")
        page_form = QtWidgets.QFormLayout(page_box)
        self.page_width = self.makeSpin(50, 4000, self.onPageEdited)
        self.page_height = self.makeSpin(50, 4000, self.onPageEdited)
        self.page_background = ColorButton()
        self.page_background.colorChanged.connect(lambda _c: self.onPageEdited())
        page_form.addRow("Width:", self.page_width)
        page_form.addRow("Height:", self.page_height)
        page_form.addRow("Background:", self.page_background)
        layout.addWidget(page_box)

        #the selected shape
        self.shape_box = QtWidgets.QGroupBox("Shape")
        shape_form = QtWidgets.QFormLayout(self.shape_box)
        self.shape_name = QtWidgets.QLineEdit()
        self.shape_name.editingFinished.connect(self.onShapeEdited)
        shape_form.addRow("Name:", self.shape_name)
        #two by two - four spin boxes in one row did not fit the panel
        geometry_grid = QtWidgets.QGridLayout()
        self.shape_x, self.shape_y = self.makeSpin(-4000, 4000, self.onShapeEdited), self.makeSpin(-4000, 4000, self.onShapeEdited)
        self.shape_w, self.shape_h = self.makeSpin(1, 4000, self.onShapeEdited), self.makeSpin(1, 4000, self.onShapeEdited)
        for index, (label, spin) in enumerate((("X", self.shape_x), ("Y", self.shape_y),
                                               ("W", self.shape_w), ("H", self.shape_h))):
            row, column = divmod(index, 2)
            geometry_grid.addWidget(QtWidgets.QLabel(label), row, column * 2)
            geometry_grid.addWidget(spin, row, column * 2 + 1)
        shape_form.addRow(geometry_grid)
        self.shape_radius = self.makeSpin(0, 500, self.onShapeEdited)
        shape_form.addRow("Corner Radius:", self.shape_radius)
        self.radius_label = shape_form.labelForField(self.shape_radius)

        fill_row = QtWidgets.QHBoxLayout()
        self.fill_enabled = QtWidgets.QCheckBox("Fill")
        self.fill_enabled.toggled.connect(lambda _c: self.onShapeEdited())
        self.fill_color = ColorButton()
        self.fill_color.colorChanged.connect(lambda _c: self.onShapeEdited())
        fill_row.addWidget(self.fill_enabled); fill_row.addWidget(self.fill_color); fill_row.addStretch()
        shape_form.addRow(fill_row)

        outline_row = QtWidgets.QHBoxLayout()
        self.outline_enabled = QtWidgets.QCheckBox("Outline")
        self.outline_enabled.toggled.connect(lambda _c: self.onShapeEdited())
        self.outline_color = ColorButton()
        self.outline_color.colorChanged.connect(lambda _c: self.onShapeEdited())
        self.outline_width = QtWidgets.QDoubleSpinBox()
        self.outline_width.setRange(0.0, 50.0)
        self.outline_width.setSingleStep(0.5)
        self.outline_width.valueChanged.connect(lambda _v: self.onShapeEdited())
        outline_row.addWidget(self.outline_enabled); outline_row.addWidget(self.outline_color)
        outline_row.addWidget(self.outline_width); outline_row.addStretch()
        self.outline_width.setPrefix("width ")
        shape_form.addRow(outline_row)

        self.opacity = QtWidgets.QDoubleSpinBox()
        self.opacity.setRange(0.0, 1.0)
        self.opacity.setSingleStep(0.1)
        self.opacity.valueChanged.connect(lambda _v: self.onShapeEdited())
        shape_form.addRow("Opacity:", self.opacity)

        self.text_box = QtWidgets.QWidget()
        text_form = QtWidgets.QFormLayout(self.text_box)
        text_form.setContentsMargins(0, 0, 0, 0)
        self.text_content = QtWidgets.QLineEdit()
        self.text_content.textEdited.connect(lambda _t: self.onShapeEdited())
        text_form.addRow("Text:", self.text_content)
        text_style = QtWidgets.QHBoxLayout()
        self.text_size = self.makeSpin(4, 200, self.onShapeEdited)
        self.text_color = ColorButton()
        self.text_color.colorChanged.connect(lambda _c: self.onShapeEdited())
        self.text_align = QtWidgets.QComboBox()
        self.text_align.addItems(["left", "center", "right"])
        self.text_align.currentIndexChanged.connect(lambda _i: self.onShapeEdited())
        self.text_bold = QtWidgets.QCheckBox("Bold")
        self.text_bold.toggled.connect(lambda _c: self.onShapeEdited())
        for widget in (QtWidgets.QLabel("Size"), self.text_size, self.text_color, self.text_align, self.text_bold):
            text_style.addWidget(widget)
        text_form.addRow(text_style)
        shape_form.addRow(self.text_box)
        layout.addWidget(self.shape_box)

        #what it does
        self.action_box = QtWidgets.QGroupBox("When Clicked")
        action_layout = QtWidgets.QVBoxLayout(self.action_box)
        self.action_type = QtWidgets.QComboBox()
        for action_type, label in ACTION_LABELS:
            self.action_type.addItem(label, action_type)
        self.action_type.currentIndexChanged.connect(self.onActionTypeChanged)
        action_layout.addWidget(self.action_type)

        self.action_pages = QtWidgets.QStackedWidget()
        self.action_pages.addWidget(QtWidgets.QLabel("Does nothing - a label or decoration. Clicks pass through "
                                                     "it to a button underneath."))
        self.action_pages.widget(0).setWordWrap(True)
        self.action_pages.addWidget(self.buildSelectPage())
        self.action_pages.addWidget(self.buildBuiltinPage())
        self.action_pages.addWidget(self.buildCodePage())
        action_layout.addWidget(self.action_pages)
        layout.addWidget(self.action_box)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.shape_box.setEnabled(False)
        self.action_box.setEnabled(False)
        return panel

    def buildSelectPage(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        #what this button selects, spelled out - the ticks alone were easy to miss
        #once the ticked controls scrolled out of view
        self.selection_summary = QtWidgets.QLabel("")
        self.selection_summary.setWordWrap(True)
        self.selection_summary.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.selection_summary)
        self.control_filter = QtWidgets.QLineEdit()
        self.control_filter.setPlaceholderText("filter controls")
        self.control_filter.textChanged.connect(self.filterControlList)
        layout.addWidget(self.control_filter)
        self.control_list = QtWidgets.QListWidget()
        self.control_list.setMinimumHeight(160)
        self.control_list.itemChanged.connect(self.onControlChecked)
        layout.addWidget(self.control_list)
        buttons = QtWidgets.QHBoxLayout()
        use_selection = QtWidgets.QPushButton("Use Viewport Selection")
        use_selection.setToolTip("Check the controls selected in the Maya scene")
        use_selection.clicked.connect(self.onUseViewportSelection)
        clear = QtWidgets.QPushButton("Clear")
        clear.clicked.connect(self.onClearControls)
        buttons.addWidget(use_selection); buttons.addWidget(clear)
        layout.addLayout(buttons)
        return page

    def buildBuiltinPage(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        self.builtin_combo = QtWidgets.QComboBox()
        for action_id, label, _ in runtime.BUILTIN_ACTIONS:
            self.builtin_combo.addItem(label, action_id)
        self.builtin_combo.currentIndexChanged.connect(self.onBuiltinChanged)
        layout.addWidget(self.builtin_combo)
        self.builtin_description = QtWidgets.QLabel("")
        self.builtin_description.setWordWrap(True)
        layout.addWidget(self.builtin_description)
        mirror_note = QtWidgets.QLabel("Mirroring pairs controls by their %s / %s side prefix and copies channel "
                                       "values as they are." % (ROSE_Names.left.prefix, ROSE_Names.right.prefix))
        mirror_note.setWordWrap(True)
        mirror_note.setStyleSheet("color: #999999;")
        layout.addWidget(mirror_note)
        return page

    def buildCodePage(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        help_label = QtWidgets.QLabel("<b>rig.node(\"name\")</b> is a rig object under the animator's namespace. "
                                      "<b>cmds</b>, <b>mel</b> and <b>rig</b> are available; a click is one undo step.")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        self.code_edit = QtWidgets.QPlainTextEdit()
        font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        self.code_edit.setFont(font)
        self.code_edit.setTabStopDistance(QtGui.QFontMetricsF(font).horizontalAdvance(" ") * 4)
        self.code_edit.setMinimumHeight(200)
        self.code_highlighter = PythonHighlighter(self.code_edit.document())
        self.code_edit.textChanged.connect(self.onCodeEdited)
        layout.addWidget(self.code_edit)
        test = QtWidgets.QPushButton("Test Run in This Scene")
        test.setToolTip("Run the code here, on the rig in this scene, with no namespace")
        test.clicked.connect(self.onTestRun)
        layout.addWidget(test)
        return page

    def makeSpin(self, minimum, maximum, callback):
        spin = QtWidgets.QSpinBox()
        spin.setRange(minimum, maximum)
        spin.valueChanged.connect(lambda _v: callback())
        return spin

# Modified plumbing

    @property
    def has_been_modified(self):
        return self._has_been_modified
    @has_been_modified.setter
    def has_been_modified(self, value):
        self._has_been_modified = value
        for callback in self._has_been_modified_listeners:
            callback()

    def setModified(self, state): self.has_been_modified = state
    def isModified(self): return self.has_been_modified
    def connectHasBeenModifiedListenerCallback(self, callback):
        self._has_been_modified_listeners.append(callback)
    def connectSelectionChangedListenerCallback(self, callback):
        self._selection_changed_listeners.append(callback)

    def activate(self):
        #the rig may have gained or lost controls while another tab was in front
        self.refreshControlList()
        self.refreshPanel()

# History

    def snapshot(self):
        return json.dumps(self.document)

    def resetHistory(self):
        self.history = [self.snapshot()]
        self.history_index = 0

    def commit(self, label = "Edit"):
        """Record the document as it is now as an undo step, if it changed."""
        self.commit_timer.stop()
        state = self.snapshot()
        if self.history and self.history[self.history_index] == state:
            return
        self.history = self.history[:self.history_index + 1] + [state]
        self.history = self.history[-HISTORY_LIMIT:]
        self.history_index = len(self.history) - 1
        self.setModified(True)
        for callback in self._selection_changed_listeners:
            callback()

    def restore(self, index):
        selected = [shape["id"] for shape in self.canvas.selectedShapes()]
        self.history_index = index
        self.document = json.loads(self.history[index])
        self.canvas.rebuild(selected)
        self.refreshPanel()
        self.setModified(True)

    def canUndo(self): return self.history_index > 0
    def canRedo(self): return self.history_index < len(self.history) - 1
    def onUndo(self):
        self.commit()
        if self.canUndo():
            self.restore(self.history_index - 1)
    def onRedo(self):
        if self.canRedo():
            self.restore(self.history_index + 1)

    def canCut(self): return False
    def canCopy(self): return False
    def canMirrorNode(self): return False
    def canDelete(self): return bool(self.canvas.selectedShapes())

# Editing shapes

    def nextShapeName(self, kind):
        names = {shape.get("name") for shape in self.document["shapes"]}
        index = 1
        while "%s%d" % (kind, index) in names:
            index += 1
        return "%s%d" % (kind, index)

    def addShape(self, shape):
        self.document["shapes"].append(shape)
        self.canvas.rebuild([shape["id"]])
        self.commit("Add %s" % shape["type"])

    def onImportSvg(self, path = None):
        """Add an SVG file's drawing to the page as shapes, selected, as one undo step."""
        if not path:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import SVG", "", "SVG (*.svg);;All (*)")
            if not path:
                return False
        page = self.document["page"]
        try:
            shapes, warnings, scale = picker_svg.importSvg(path, page["width"], page["height"])
        except Exception as error:
            self.showStatus("Could not import '%s': %s" % (os.path.basename(path), error), False)
            return False
        if not shapes:
            self.showStatus("Nothing in '%s' could be turned into shapes." % os.path.basename(path), False)
            return False
        self.document["shapes"] += shapes
        self.canvas.rebuild([shape["id"] for shape in shapes])
        self.commit("Import SVG")
        message = "Imported %d shape(s) from %s" % (len(shapes), os.path.basename(path))
        if scale < 1.0:
            message += ", scaled to %d%% to fit the page" % round(scale * 100)
        if warnings:
            message += ". Note: " + "; ".join(warnings)
        self.showStatus(message, True)
        return True

    def onDelete(self):
        selected = {shape["id"] for shape in self.canvas.selectedShapes()}
        if not selected:
            return
        self.document["shapes"] = [s for s in self.document["shapes"] if s["id"] not in selected]
        self.canvas.rebuild()
        self.commit("Delete")

    def onDuplicate(self):
        clones = [document_model.duplicateShape(s) for s in self.canvas.selectedShapes()]
        if not clones:
            return
        self.document["shapes"] += clones
        self.canvas.rebuild([c["id"] for c in clones])
        self.commit("Duplicate")

    def onReorder(self, step):
        """Move the selected shapes one place up (1) or down (-1) the drawing order."""
        selected = {shape["id"] for shape in self.canvas.selectedShapes()}
        shapes = self.document["shapes"]
        indices = range(len(shapes) - 2, -1, -1) if step > 0 else range(1, len(shapes))
        for index in indices:
            other = index + step
            if shapes[index]["id"] in selected and shapes[other]["id"] not in selected:
                shapes[index], shapes[other] = shapes[other], shapes[index]
        self.canvas.rebuild(selected)
        self.commit("Reorder")

    def onToggleSnap(self):
        self.canvas.snap = self.snap_action.isChecked()
        self.canvas.update()

    def onToolChanged(self, tool):
        if tool in self.tool_actions:
            self.tool_actions[tool].setChecked(True)

    def onShapesEdited(self, live):
        """A drag on the canvas moved or resized shapes."""
        self.refreshPanel()
        if not live:
            self.commit("Move")

# The panel

    def selectedShape(self):
        shapes = self.canvas.selectedShapes()
        return shapes[0] if len(shapes) == 1 else None

    def onSelectionChanged(self):
        self.refreshPanel()
        for callback in self._selection_changed_listeners:
            callback()

    def refreshPanel(self):
        self.updating_panel = True
        try:
            page = self.document["page"]
            self.page_width.setValue(int(page["width"]))
            self.page_height.setValue(int(page["height"]))
            self.page_background.setColor(page.get("background", "#2B2B2B"))

            shape = self.selectedShape()
            self.shape_box.setEnabled(shape is not None)
            self.action_box.setEnabled(shape is not None)
            if shape is None:
                count = len(self.canvas.selectedShapes())
                self.shape_box.setTitle("Shape - select one shape to edit it" if not count
                                        else "%d shapes selected - select one to edit it" % count)
                self.action_box.setTitle("When Clicked")
                self.clearShapeFields()
                return
            self.action_box.setTitle("When '%s' Is Clicked" % shape.get("name", "shape"))
            self.shape_box.setTitle("Shape - %s" % shape["type"])
            self.shape_name.setText(shape.get("name", ""))
            for spin, key in ((self.shape_x, "x"), (self.shape_y, "y"), (self.shape_w, "w"), (self.shape_h, "h")):
                spin.setValue(int(round(shape[key])))
            self.shape_radius.setValue(int(shape.get("radius", 0)))
            self.shape_radius.setVisible(shape["type"] == "rect")
            if self.radius_label:
                self.radius_label.setVisible(shape["type"] == "rect")
            self.fill_enabled.setChecked(shape["fill"]["enabled"])
            self.fill_color.setColor(shape["fill"]["color"])
            self.outline_enabled.setChecked(shape["outline"]["enabled"])
            self.outline_color.setColor(shape["outline"]["color"])
            self.outline_width.setValue(shape["outline"]["width"])
            self.opacity.setValue(shape.get("opacity", 1.0))
            self.text_box.setVisible(shape["type"] == "text")
            text = shape["text"]
            if self.text_content.text() != text["content"]:
                self.text_content.setText(text["content"])
            self.text_size.setValue(int(text["size"]))
            self.text_color.setColor(text["color"])
            self.text_align.setCurrentText(text.get("align", "center"))
            self.text_bold.setChecked(bool(text.get("bold")))

            action = shape["action"]
            index = self.action_type.findData(action.get("type", "none"))
            self.action_type.setCurrentIndex(max(index, 0))
            self.action_pages.setCurrentIndex(max(index, 0))
            self.builtin_combo.setCurrentIndex(max(self.builtin_combo.findData(action.get("builtin")), 0))
            self.updateBuiltinDescription()
            if self.code_edit.toPlainText() != action.get("code", ""):
                self.code_edit.setPlainText(action.get("code", ""))
            self.checkAssignedControls(action.get("controls", []))
            self.updateSelectionSummary(action.get("controls", []))
        finally:
            self.updating_panel = False

    def clearShapeFields(self):
        """Empty the shape and action fields - a disabled panel still showing the
        last shape's values read as if they belonged to the new selection."""
        self.shape_name.clear()
        for spin in (self.shape_x, self.shape_y, self.shape_w, self.shape_h, self.shape_radius):
            spin.setValue(spin.minimum() if spin.minimum() > 0 else 0)
        self.text_content.clear()
        self.action_type.setCurrentIndex(0)
        self.action_pages.setCurrentIndex(0)
        self.code_edit.clear()
        self.checkAssignedControls([])
        self.selection_summary.clear()

    def updateSelectionSummary(self, control_ids):
        names = {control_id: name for control_id, name, _ in self.getRigControls()}
        known = [names[str(i)] for i in control_ids if str(i) in names]
        missing = len(control_ids) - len(known)
        if not control_ids:
            text = "<b>Selects:</b> nothing yet - tick controls below, or use the viewport selection"
        else:
            text = "<b>Selects:</b> " + ", ".join(known)
            if missing:
                text += " <span style='color:#E0A030'>(+%d no longer in the rig)</span>" % missing
        self.selection_summary.setText(text)

    def onPageEdited(self):
        if self.updating_panel:
            return
        page = self.document["page"]
        page.update(width = self.page_width.value(), height = self.page_height.value(),
                    background = self.page_background.color)
        self.canvas.rebuild([s["id"] for s in self.canvas.selectedShapes()])
        self.commit_timer.start(COMMIT_DELAY_MS)

    def onShapeEdited(self):
        shape = self.selectedShape()
        if self.updating_panel or shape is None:
            return
        shape["name"] = self.shape_name.text().strip() or shape.get("name", "")
        document_model.resizeShape(shape, self.shape_x.value(), self.shape_y.value(),
                                   self.shape_w.value(), self.shape_h.value())
        shape["radius"] = self.shape_radius.value()
        shape["fill"].update(enabled = self.fill_enabled.isChecked(), color = self.fill_color.color)
        shape["outline"].update(enabled = self.outline_enabled.isChecked(), color = self.outline_color.color,
                                width = self.outline_width.value())
        shape["opacity"] = self.opacity.value()
        shape["text"].update(content = self.text_content.text(), size = self.text_size.value(),
                             color = self.text_color.color, align = self.text_align.currentText(),
                             bold = self.text_bold.isChecked())
        self.canvas.items_by_id[shape["id"]].syncFromShape()
        self.commit_timer.start(COMMIT_DELAY_MS)

# Actions

    def onActionTypeChanged(self, index):
        self.action_pages.setCurrentIndex(index)
        shape = self.selectedShape()
        if self.updating_panel or shape is None:
            return
        #one purpose per button: choosing a kind is all it takes, the others' settings stay
        #on the shape in case the choice is changed back, but only this one is used or exported
        shape["action"]["type"] = self.action_type.itemData(index)
        self.updateShapeTooltip(shape)
        self.commit("Change action")

    def onBuiltinChanged(self, index):
        self.updateBuiltinDescription()
        shape = self.selectedShape()
        if self.updating_panel or shape is None:
            return
        shape["action"]["builtin"] = self.builtin_combo.itemData(index)
        self.updateShapeTooltip(shape)
        self.commit("Change action")

    def updateBuiltinDescription(self):
        descriptions = {action_id: description for action_id, _, description in runtime.BUILTIN_ACTIONS}
        self.builtin_description.setText(descriptions.get(self.builtin_combo.currentData(), ""))

    def onCodeEdited(self):
        shape = self.selectedShape()
        if self.updating_panel or shape is None:
            return
        shape["action"]["code"] = self.code_edit.toPlainText()
        self.commit_timer.start(COMMIT_DELAY_MS)

    def getRigControls(self):
        """[(control id, name, component label)] for every control in the rig graph."""
        controls = []
        for group in self.getScene().getControlDict().values():
            for entry in group["controls"]:
                controls.append((str(entry["id"]), entry["name"], group["label"]))
        return controls

    def refreshControlList(self):
        self.control_list.blockSignals(True)
        self.control_list.clear()
        for control_id, name, label in self.getRigControls():
            item = QtWidgets.QListWidgetItem(name)
            item.setData(CONTROL_ID_ROLE, control_id)
            item.setToolTip(label)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.control_list.addItem(item)
        self.control_list.blockSignals(False)
        shape = self.selectedShape()
        if shape is not None:
            self.checkAssignedControls(shape["action"].get("controls", []))
        self.filterControlList(self.control_filter.text())

    def checkAssignedControls(self, control_ids):
        """Tick a button's controls, and bring them to the top of the list - in
        rig order among themselves - so they are in view without scrolling."""
        wanted = {str(control_id) for control_id in control_ids}
        self.control_list.blockSignals(True)
        items = [self.control_list.takeItem(0) for _ in range(self.control_list.count())]
        order = {control_id: index for index, (control_id, _, _) in enumerate(self.getRigControls())}
        items.sort(key = lambda item: (item.data(CONTROL_ID_ROLE) not in wanted,
                                       order.get(item.data(CONTROL_ID_ROLE), len(order))))
        for item in items:
            item.setCheckState(QtCore.Qt.Checked if item.data(CONTROL_ID_ROLE) in wanted else QtCore.Qt.Unchecked)
            self.control_list.addItem(item)
        self.control_list.blockSignals(False)
        self.filterControlList(self.control_filter.text())

    def filterControlList(self, text):
        text = text.lower()
        for index in range(self.control_list.count()):
            item = self.control_list.item(index)
            item.setHidden(bool(text) and text not in item.text().lower())

    def onControlChecked(self, item):
        shape = self.selectedShape()
        if self.updating_panel or shape is None:
            return
        shape["action"]["controls"] = [self.control_list.item(i).data(CONTROL_ID_ROLE)
                                       for i in range(self.control_list.count())
                                       if self.control_list.item(i).checkState() == QtCore.Qt.Checked]
        self.updateSelectionSummary(shape["action"]["controls"])
        self.updateShapeTooltip(shape)
        self.commit("Assign controls")

    def onUseViewportSelection(self):
        shape = self.selectedShape()
        if shape is None:
            return
        by_name = {name: control_id for control_id, name, _ in self.getRigControls()}
        chosen = []
        for node in MC.getViewportSelection():
            short = node.split("|")[-1].split(":")[-1]
            if short in by_name:
                chosen.append(by_name[short])
        if not chosen:
            self.showStatus("None of the selected objects are controls of this rig.", False)
            return
        shape["action"]["controls"] = chosen
        self.checkAssignedControls(chosen)
        self.updateSelectionSummary(chosen)
        self.updateShapeTooltip(shape)
        self.commit("Assign controls")
        self.showStatus("%d control(s) assigned." % len(chosen), True)

    def onClearControls(self):
        shape = self.selectedShape()
        if shape is None:
            return
        shape["action"]["controls"] = []
        self.checkAssignedControls([])
        self.updateSelectionSummary([])
        self.updateShapeTooltip(shape)
        self.commit("Assign controls")

    def onTestRun(self):
        """Run the selected shape's action here, as the picker would - with no
        namespace, on the rig in this scene."""
        shape = self.selectedShape()
        if shape is None:
            return
        self.commit()
        data, _ = self.resolveData()
        resolved = next((s for s in data["shapes"] if s["id"] == shape["id"]), shape)
        ok, message = runtime.runAction(resolved, runtime.RigContext(data, ""))
        self.showStatus(message or "Done.", ok)

    def describeAction(self, shape):
        action = shape.get("action") or {}
        kind = action.get("type", "none")
        if kind == "select":
            names = {control_id: name for control_id, name, _ in self.getRigControls()}
            known = [names.get(str(i), "(missing)") for i in action.get("controls", [])]
            return "%s - selects: %s" % (shape.get("name"), ", ".join(known) if known else "nothing yet")
        if kind == "builtin":
            return "%s - %s" % (shape.get("name"), runtime.BUILTIN_LABELS.get(action.get("builtin"), ""))
        if kind == "code":
            first = next((line for line in action.get("code", "").splitlines()
                          if line.strip() and not line.strip().startswith("#")), "")
            return "%s - runs code: %s" % (shape.get("name"), first.strip()[:60])
        return "%s - does nothing (label or decoration)" % shape.get("name")

    def updateShapeTooltip(self, shape):
        item = self.canvas.items_by_id.get(shape["id"])
        if item is not None:
            item.setToolTip(self.describeAction(shape))

    def showStatus(self, message, ok):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("" if ok else "color: #E0A030;")

# Export

    def resolveData(self):
        """The picker's data as the exported script runs on it - see
        picker_document.resolveDocument. Returns (data, [problems])."""
        controls = self.getRigControls()
        names = {control_id: name for control_id, name, _ in controls}
        rig_name = self.getScene().properties.getRigName()
        if not rig_name or rig_name == "Undefined":
            rig_name = "Rig"
        return document_model.resolveDocument(self.document, names, [name for _, name, _ in controls], rig_name,
                                              [(ROSE_Names.left.prefix, ROSE_Names.right.prefix)])

    def exportPicker(self, directory):
        """Write the picker script into a directory. Returns (success, message)."""
        self.commit()
        if not self.document["shapes"]:
            return True, "No picker drawn - nothing written"
        data, problems = self.resolveData()
        path = os.path.join(directory, "%s_picker.py" % data["rig_name"])
        try:
            document_model.writePickerScript(data, path)
        except Exception as error:
            return False, "Could not write the picker: %s" % error
        message = "Picker written to %s" % path
        if problems:
            message += " - %d problem(s): %s" % (len(problems), "; ".join(problems))
        return True, message

# Project file

    def onOpenFile(self, file_path):
        if os.path.isdir(file_path):
            graph_file = findProjectGraphFile(file_path)
            if graph_file is not None:
                self.loadFile(graph_file)
            else:
                self.onNewFile()
        elif os.path.isfile(file_path):
            self.loadFile(file_path)
        return True

    def loadFile(self, file_path):
        self.failed_load_path = None
        try:
            with open(file_path, "r") as file:
                self.deserialize(json.loads(file.read()))
        except Exception as error:
            #a corrupted file shouldn't take down the whole project open
            log.error("PICKERTAB:: --loadFile:: could not load '%s': %s - starting empty" % (file_path, error))
            self.failed_load_path = file_path
            self.onNewFile()
            return False
        return True

    def onSaveFile(self, file_name):
        #a failed load left this tab empty while the real data is still on disk
        if self.failed_load_path is not None:
            log.error("PICKERTAB:: --onSaveFile:: Not saving: '%s' could not be read earlier, so this tab is empty "
                      "and saving would overwrite the project's real data." % self.failed_load_path)
            return False
        self.commit()
        with open(file_name, "w") as file:
            file.write(json.dumps(self.serialize(), indent = 4))
        self.setModified(False)
        return True

    def onNewFile(self):
        self.document = document_model.newDocument()
        self.canvas.rebuild()
        self.resetHistory()
        self.refreshPanel()
        self.setModified(False)

    def serialize(self):
        return OrderedDict([("id", self.id), ("document", copy.deepcopy(self.document))])

    def deserialize(self, data, hashmap = {}, restore_id = True):
        if restore_id and "id" in data:
            self.id = data["id"]
        self.document = data.get("document") or document_model.newDocument()
        self.canvas.rebuild()
        self.resetHistory()
        self.refreshPanel()
        self.setModified(False)
        return True
