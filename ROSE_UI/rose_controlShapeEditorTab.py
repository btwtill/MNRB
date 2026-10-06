from collections import OrderedDict
import json, os
from PySide6 import QtWidgets #type: ignore
from PySide6.QtCore import Qt, QSize #type: ignore
from PySide6.QtGui import QIcon, QColor #type: ignore
from MNRB.ROSE_Data.rose_Editor_Serializable import Serializable #type: ignore
from MNRB.ROSE_Controls import control_shape_library #type: ignore
from MNRB.ROSE_Controls.control_shape_library import (GENERAL_LIBRARY_ID, DEFAULT_FACING, #type: ignore
                                                      FACING_AXES, getFacing)
from MNRB.ROSE_UI.control_shape_Editor_UI.control_shape_preview import buildShapePreviewPixmap, LINE_COLOR #type: ignore
from MNRB.ROSE_UI.rose_ui_utils import findProjectGraphFile #type: ignore
from MNRB.ROSE_UI.UI_GraphicComponents.list_group_item import ExpandableGroupsMixin #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")

DEFAULT_SHAPE_LABEL = "Default"
PREVIEW_SIZE = 96

#on each control row, which control it is and what it is called
CONTROL_ID_ROLE = Qt.ItemDataRole.UserRole
CONTROL_NAME_ROLE = Qt.ItemDataRole.UserRole + 1

#the editors on a row, and the header above them, share these
SHAPE_COLUMN_WIDTH = 170
SCALE_COLUMN_WIDTH = 72
FACING_COLUMN_WIDTH = 64
ROW_HEIGHT = 30

#rig library shapes are drawn in their own colour, so the two kinds tell apart
RIG_LINE_COLOR = QColor("#60C8E0")


def makeShapeKey(library_id, shape_name):
    """One string naming a shape in a particular library - shape names are only
    unique within a library, and a general and a rig shape may share one."""
    return "%s:%s" % (library_id or GENERAL_LIBRARY_ID, shape_name)


def splitShapeKey(shape_key):
    library_id, _, shape_name = shape_key.partition(":")
    return library_id, shape_name


class AddShapeDialog(QtWidgets.QDialog):
    """A name, and which library the new shape goes into."""

    def __init__(self, library_ids, default_library_id, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Add Control Shape")

        layout = QtWidgets.QFormLayout(self)

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Letters, digits and underscores")
        layout.addRow("Name:", self.name_edit)

        self.library_combo = QtWidgets.QComboBox()
        for library_id in library_ids:
            self.library_combo.addItem(control_shape_library.getLibraryLabel(library_id), library_id)
        self.library_combo.setCurrentIndex(max(self.library_combo.findData(default_library_id), 0))
        self.library_combo.setToolTip("General: shared by every project.\n"
                                      "Rig: stored with the node pack, only for this rig.")
        layout.addRow("Library:", self.library_combo)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def getName(self):
        return self.name_edit.text().strip()

    def getLibraryId(self):
        return self.library_combo.currentData()


class ControlShapeRow(QtWidgets.QWidget):
    """One control: its name, then the shape, scale and facing editors."""

    def __init__(self, control_name, shape_combo, scale_spinbox, facing_combo, parent = None):
        super().__init__(parent)
        #the list's own selection highlight shows through
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(22, 2, 6, 2)
        layout.setSpacing(6)

        name_label = QtWidgets.QLabel(control_name)
        name_label.setToolTip(control_name)
        name_label.setMinimumWidth(60)
        layout.addWidget(name_label, 1)

        shape_combo.setFixedWidth(SHAPE_COLUMN_WIDTH)
        scale_spinbox.setFixedWidth(SCALE_COLUMN_WIDTH)
        facing_combo.setFixedWidth(FACING_COLUMN_WIDTH)
        layout.addWidget(shape_combo)
        layout.addWidget(scale_spinbox)
        layout.addWidget(facing_combo)


class ControlShapeList(ExpandableGroupsMixin, QtWidgets.QListWidget):
    """The controls, grouped by component like the Skin and Attributes tabs'
    lists - collapsible headers, rows underneath."""

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        #always there, so the column header above lines up with the row editors
        #whether or not the list is long enough to scroll
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def addGroup(self, label, entry_ids):
        header_item = QtWidgets.QListWidgetItem(self)
        group_item = self.createGroupItem(label, entry_ids)
        group_item.adjustSize()
        header_item.setSizeHint(group_item.sizeHint())
        header_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.setItemWidget(header_item, group_item)
        return group_item

    def addControlRow(self, group_item, control_id, control_name, row_widget):
        item = QtWidgets.QListWidgetItem(self)
        item.setData(CONTROL_ID_ROLE, control_id)
        item.setData(CONTROL_NAME_ROLE, control_name)
        item.setSizeHint(QSize(0, ROW_HEIGHT))
        self.setItemWidget(item, row_widget)
        group_item.addListItem(item)
        return item


def buildColumnHeader():
    """"Control / Shape / Scale / Facing" over the list, lined up with the row editors."""
    header = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout(header)
    #the rows' own right margin, plus the list's frame and its scrollbar
    layout.setContentsMargins(24, 2, 8 + QtWidgets.QApplication.style().pixelMetric(
        QtWidgets.QStyle.PM_ScrollBarExtent), 2)
    layout.setSpacing(6)

    for text, width in (("Control", None), ("Shape", SHAPE_COLUMN_WIDTH), ("Scale", SCALE_COLUMN_WIDTH),
                        ("Facing", FACING_COLUMN_WIDTH)):
        label = QtWidgets.QLabel(text)
        label.setStyleSheet("color: #999999; font-weight: bold;")
        if width is None:
            layout.addWidget(label, 1)
        else:
            label.setFixedWidth(width)
            layout.addWidget(label)
    return header


class rose_ControlShapeEditorTab(QtWidgets.QMainWindow, Serializable):
    """Which library shape each control is drawn with, and at what scale.

    The assignments are this project's. The shapes come from the general library,
    shared by every project, and from the rig library of each node pack the
    project's graph uses (see control_shape_library). They take effect whenever a
    control is drawn - any component build, from anywhere - because they are
    pushed into control_shape_library's registry, which the controls read, rather
    than applied by this tab. "Apply to Rig" only redraws controls that are
    already built, so a change shows without rebuilding.
    """

    def __init__(self, node_editor, parent = None):
        QtWidgets.QMainWindow.__init__(self, parent)
        Serializable.__init__(self)

        self.is_tab_widget = True
        self.node_editor = node_editor

        #{str(control id): {"shape": name or None, "library": id, "scale": float, "facing": axis,
        #"label": control name}}. The label is only for reading the saved file -
        #the id is what matches.
        self.assignments = {}
        self.failed_load_path = None
        #where the Add dialog points next time - the library last added to
        self.last_library_id = GENERAL_LIBRARY_ID

        self._has_been_modified = False
        self._has_been_modified_listeners = []

        self.initUI()
        self.pushAssignments()

    def getScene(self):
        return self.node_editor.central_widget.scene

    def initUI(self):
        self.addToolBar(self.buildToolbar())

        splitter = QtWidgets.QSplitter(Qt.Horizontal)

        control_panel = QtWidgets.QWidget()
        control_layout = QtWidgets.QVBoxLayout(control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(2)
        control_layout.addWidget(buildColumnHeader())

        self.control_list = ControlShapeList()
        control_layout.addWidget(self.control_list)
        splitter.addWidget(control_panel)

        library_panel = QtWidgets.QWidget()
        library_layout = QtWidgets.QVBoxLayout(library_panel)
        library_layout.setContentsMargins(0, 0, 0, 0)
        library_layout.addWidget(QtWidgets.QLabel("Shape Library - double-click to assign to the selected controls"))

        self.library_list = QtWidgets.QListWidget()
        self.library_list.setViewMode(QtWidgets.QListView.IconMode)
        self.library_list.setIconSize(QSize(PREVIEW_SIZE, PREVIEW_SIZE))
        self.library_list.setResizeMode(QtWidgets.QListView.Adjust)
        self.library_list.setMovement(QtWidgets.QListView.Static)
        self.library_list.setSpacing(6)
        self.library_list.itemDoubleClicked.connect(self.onLibraryItemDoubleClicked)
        self.library_list.itemSelectionChanged.connect(self.updateToolbarState)
        library_layout.addWidget(self.library_list)

        splitter.addWidget(library_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        self.setCentralWidget(splitter)

    def buildToolbar(self):
        toolbar = QtWidgets.QToolBar("Control Shapes")
        toolbar.setMovable(False)

        self.add_action = toolbar.addAction("Add From Selection", self.onAddShape)
        self.add_action.setToolTip("Store the selected curve object, normalised to the unit size, in the general "
                                   "library or in the rig library of one of this project's node packs")
        self.overwrite_action = toolbar.addAction("Overwrite Selected", self.onOverwriteShape)
        self.overwrite_action.setToolTip("Replace the selected library shape with the selected curve object")
        self.remove_action = toolbar.addAction("Remove Selected", self.onRemoveShape)
        self.remove_action.setToolTip("Delete the selected library shape - controls using it fall back to their default")

        toolbar.addSeparator()
        self.clear_action = toolbar.addAction("Clear Assignment", self.onClearSelectedAssignments)
        self.clear_action.setToolTip("Back to the default shape and scale for the selected controls")
        self.apply_action = toolbar.addAction("Apply to Rig", self.onApplyToRig)
        self.apply_action.setToolTip("Redraw every built control with its assigned shape, without a rebuild")
        self.clean_action = toolbar.addAction("Remove Unused", self.onRemoveUnusedAssignments)
        self.clean_action.setToolTip("Forget assignments for controls that no longer exist in the rig graph")

        return toolbar

    def updateToolbarState(self):
        has_library_selection = self.library_list.currentItem() is not None
        self.overwrite_action.setEnabled(has_library_selection)
        self.remove_action.setEnabled(has_library_selection)

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

# Refreshing

    def activate(self):
        #the rig graph may have gained or lost controls while another tab was in front
        self.refresh()

    def refresh(self):
        self.refreshLibrary()
        self.refreshControlTree()
        self.updateToolbarState()

    def getLibraryIds(self):
        """General first, then the rig library of every node pack this project's
        graph draws components from - plus any pack an assignment still points at,
        so its shapes stay listed if the last component using it was removed."""
        type_ids = [getattr(node, "type_id", "") for node in self.getScene().nodes]
        rig_ids = control_shape_library.getRigLibraryIds(type_ids)

        for assignment in self.assignments.values():
            library_id = assignment.get("library")
            if library_id and library_id != GENERAL_LIBRARY_ID and library_id not in rig_ids \
                    and control_shape_library.getLibraryDirectory(library_id) is not None:
                rig_ids.append(library_id)

        return [GENERAL_LIBRARY_ID] + rig_ids

    def getAllShapeKeys(self):
        """(shape key, display label) for every shape in every available library."""
        entries = []
        for library_id in self.getLibraryIds():
            for shape_name in control_shape_library.getShapeNames(library_id):
                entries.append((makeShapeKey(library_id, shape_name),
                                self.getShapeLabel(library_id, shape_name)))
        return entries

    def getShapeLabel(self, library_id, shape_name):
        if library_id == GENERAL_LIBRARY_ID:
            return shape_name
        return "%s  [%s]" % (shape_name, control_shape_library.getLibraryLabel(library_id))

    def refreshLibrary(self):
        selected = self.getSelectedLibraryShape()
        self.library_list.clear()

        for library_id in self.getLibraryIds():
            is_rig = library_id != GENERAL_LIBRARY_ID
            library_label = control_shape_library.getLibraryLabel(library_id)

            for shape_name in control_shape_library.getShapeNames(library_id):
                pixmap = buildShapePreviewPixmap(control_shape_library.getShapePreview(shape_name, library_id),
                                                 PREVIEW_SIZE, RIG_LINE_COLOR if is_rig else LINE_COLOR)
                item = QtWidgets.QListWidgetItem(QIcon(pixmap), "%s\n%s" % (shape_name, library_label))
                item.setToolTip("%s - %s library" % (shape_name, library_label))
                shape_key = makeShapeKey(library_id, shape_name)
                item.setData(Qt.ItemDataRole.UserRole, shape_key)
                self.library_list.addItem(item)
                if shape_key == selected:
                    self.library_list.setCurrentItem(item)

    def refreshControlTree(self):
        #a rebuild keeps what the user had open, selected and scrolled to - the
        #list is rebuilt after every assignment made from the library
        selected_ids = {item.data(CONTROL_ID_ROLE) for item in self.getSelectedControlItems()}
        scroll_position = self.control_list.verticalScrollBar().value()
        self.control_list.clear()

        shape_entries = self.getAllShapeKeys()

        for group in self.getScene().getControlDict().values():
            if not group["controls"]:
                continue

            group_item = self.control_list.addGroup(group["label"], [entry["id"] for entry in group["controls"]])

            for control_entry in group["controls"]:
                control_id = str(control_entry["id"])
                control_name = control_entry["name"]
                assignment = self.assignments.get(control_id, {})

                current_key = (makeShapeKey(assignment.get("library"), assignment["shape"])
                               if assignment.get("shape") else None)
                row = ControlShapeRow(control_name,
                                      self.buildShapeCombo(control_id, control_name, current_key, shape_entries),
                                      self.buildScaleSpinBox(control_id, control_name, assignment.get("scale", 1.0)),
                                      self.buildFacingCombo(control_id, control_name,
                                                            getFacing(assignment.get("facing"))))

                item = self.control_list.addControlRow(group_item, control_id, control_name, row)
                if control_id in selected_ids:
                    item.setSelected(True)

        self.control_list.updateGeometries()
        self.control_list.verticalScrollBar().setValue(scroll_position)

    def buildShapeCombo(self, control_id, control_name, current_key, shape_entries):
        combo = QtWidgets.QComboBox()
        combo.setFocusPolicy(Qt.StrongFocus)
        combo.wheelEvent = lambda event: event.ignore()
        combo.addItem(DEFAULT_SHAPE_LABEL, None)
        for shape_key, label in shape_entries:
            combo.addItem(label, shape_key)

        if current_key and combo.findData(current_key) < 0:
            #assigned, but gone from its library - shown rather than silently dropped
            library_id, shape_name = splitShapeKey(current_key)
            combo.addItem("%s (missing)" % self.getShapeLabel(library_id, shape_name), current_key)

        index = combo.findData(current_key) if current_key else 0
        combo.setCurrentIndex(max(index, 0))
        combo.currentIndexChanged.connect(
            lambda _index, combo = combo: self.setAssignment(control_id, control_name, shape_key = combo.currentData()))
        return combo

    def buildScaleSpinBox(self, control_id, control_name, current_scale):
        spinbox = QtWidgets.QDoubleSpinBox()
        #a scroll over the list must scroll the list, not change a scale on the way
        spinbox.setFocusPolicy(Qt.StrongFocus)
        spinbox.wheelEvent = lambda event: event.ignore()
        spinbox.setDecimals(3)
        spinbox.setRange(0.01, 100.0)
        spinbox.setSingleStep(0.1)
        spinbox.setValue(current_scale)
        spinbox.valueChanged.connect(
            lambda value: self.setAssignment(control_id, control_name, scale = value))
        return spinbox

    def buildFacingCombo(self, control_id, control_name, current_facing):
        combo = QtWidgets.QComboBox()
        combo.setFocusPolicy(Qt.StrongFocus)
        combo.wheelEvent = lambda event: event.ignore()
        for axis in FACING_AXES:
            combo.addItem(axis, axis)
        combo.setCurrentIndex(max(combo.findData(current_facing), 0))
        combo.setToolTip("The control axis the shape's front points along. A shape's front is the way it "
                         "faced when stored - its +Y, the way a circle drawn on the grid faces - so +Y "
                         "draws it as stored, and one stored shape serves a control facing any way")
        combo.currentIndexChanged.connect(
            lambda _index, combo = combo: self.setAssignment(control_id, control_name, facing = combo.currentData()))
        return combo

# Assigning

    _UNCHANGED = object()

    def setAssignment(self, control_id, control_name, shape_key = _UNCHANGED, scale = _UNCHANGED,
                      facing = _UNCHANGED):
        """shape_key: a makeShapeKey() string, or None for the default shape."""
        assignment = dict(self.assignments.get(control_id, {"shape": None, "scale": 1.0}))
        if shape_key is not self._UNCHANGED:
            if shape_key:
                assignment["library"], assignment["shape"] = splitShapeKey(shape_key)
            else:
                assignment["shape"] = None
                assignment.pop("library", None)
        if scale is not self._UNCHANGED:
            assignment["scale"] = float(scale)
        if facing is not self._UNCHANGED:
            assignment["facing"] = getFacing(facing)
        assignment["label"] = control_name

        #the default shape at the default scale, facing as stored, is no assignment at all
        if not assignment["shape"] and abs(assignment["scale"] - 1.0) < 1e-9 \
                and getFacing(assignment.get("facing")) == DEFAULT_FACING:
            self.assignments.pop(control_id, None)
        else:
            self.assignments[control_id] = assignment

        self.pushAssignments()
        self.setModified(True)

    def pushAssignments(self):
        control_shape_library.setAssignments(self.assignments)

    def getSelectedControlItems(self):
        return [item for item in self.control_list.selectedItems()
                if item.data(CONTROL_ID_ROLE) is not None]

    def getSelectedLibraryShape(self):
        """The selected library item's shape key, or None."""
        item = self.library_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def onLibraryItemDoubleClicked(self, item):
        control_items = self.getSelectedControlItems()
        if not control_items:
            self.showMessage("Select one or more controls on the left first.")
            return

        shape_key = item.data(Qt.ItemDataRole.UserRole)
        for control_item in control_items:
            self.setAssignment(control_item.data(CONTROL_ID_ROLE),
                               control_item.data(CONTROL_NAME_ROLE), shape_key = shape_key)
        self.refreshControlTree()

    def onClearSelectedAssignments(self):
        for control_item in self.getSelectedControlItems():
            self.assignments.pop(control_item.data(CONTROL_ID_ROLE), None)
        self.pushAssignments()
        self.setModified(True)
        self.refreshControlTree()

    def onRemoveUnusedAssignments(self):
        existing = {str(entry["id"]) for group in self.getScene().getControlDict().values()
                    for entry in group["controls"]}
        unused = [control_id for control_id in self.assignments if control_id not in existing]
        for control_id in unused:
            del self.assignments[control_id]

        if unused:
            self.pushAssignments()
            self.setModified(True)
        self.showMessage("Removed %d unused assignment(s)." % len(unused))

# Library actions

    def onAddShape(self):
        library_ids = self.getLibraryIds()
        dialog = AddShapeDialog(library_ids, self.last_library_id, self)
        if dialog.exec() != QtWidgets.QDialog.Accepted or not dialog.getName():
            return

        self.last_library_id = dialog.getLibraryId()
        self.storeShape(dialog.getName(), dialog.getLibraryId(), overwrite = False)

    def onOverwriteShape(self):
        shape_key = self.getSelectedLibraryShape()
        if not shape_key:
            return
        library_id, shape_name = splitShapeKey(shape_key)
        if self.confirm("Replace '%s' in the %s library with the selected curve object?"
                        % (shape_name, control_shape_library.getLibraryLabel(library_id))):
            self.storeShape(shape_name, library_id, overwrite = True)

    def storeShape(self, shape_name, library_id, overwrite):
        success, message = control_shape_library.addShapeFromSelection(shape_name, library_id, overwrite = overwrite)
        if not success:
            self.showMessage(message, is_error = True)
            return
        log.info("CONTROLSHAPETAB:: ", message)
        self.refresh()

    def onRemoveShape(self):
        shape_key = self.getSelectedLibraryShape()
        if not shape_key:
            return
        library_id, shape_name = splitShapeKey(shape_key)

        users = [assignment["label"] for assignment in self.assignments.values()
                 if assignment.get("shape") == shape_name
                 and (assignment.get("library") or GENERAL_LIBRARY_ID) == library_id]
        warning = ("\n\n%d control(s) in this project use it and will fall back to their default shape."
                   % len(users)) if users else ""
        scope = ("The general library is shared by every project." if library_id == GENERAL_LIBRARY_ID
                 else "The rig library belongs to the node pack.")
        if not self.confirm("Delete '%s' from the %s library? %s%s"
                            % (shape_name, control_shape_library.getLibraryLabel(library_id), scope, warning)):
            return

        success, message = control_shape_library.removeShape(shape_name, library_id)
        if not success:
            self.showMessage(message, is_error = True)
        self.refresh()

# Applying

    def onApplyToRig(self):
        """Redraw every built control's shape. Returns (success, message) so the
        pipeline step can use it."""
        if not control_shape_library.isEnabled():
            log.info("CONTROLSHAPETAB:: --onApplyToRig:: control shapes are disabled in the pipeline - "
                     "controls are redrawn with their default shapes")

        redrawn = 0
        failed = []
        for node in self.getScene().nodes:
            for component_control in node.controls:
                try:
                    if component_control.control_shape.redraw():
                        redrawn += 1
                except Exception as error:
                    failed.append("%s: %s" % (component_control.name, error))

        for failure in failed:
            log.warning("CONTROLSHAPETAB:: --onApplyToRig:: could not redraw ", failure)

        message = "Redrew %d control(s)%s" % (redrawn, (", %d failed" % len(failed)) if failed else "")
        return not failed, message

# Helpers

    def confirm(self, text):
        return QtWidgets.QMessageBox.question(self, "Control Shapes", text) == QtWidgets.QMessageBox.Yes

    def showMessage(self, text, is_error = False):
        if is_error:
            QtWidgets.QMessageBox.warning(self, "Control Shapes", text)
        else:
            QtWidgets.QMessageBox.information(self, "Control Shapes", text)

# Edit menu contract - nothing here is cut, copied or undone

    def canCut(self): return False
    def canCopy(self): return False
    def canMirrorNode(self): return False
    def canUndo(self): return False
    def canRedo(self): return False
    def canDelete(self): return False
    def onDelete(self): pass
    def onUndo(self): pass
    def onRedo(self): pass

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
        except Exception as e:
            #a corrupted file shouldn't take down the whole project open
            log.error("CONTROLSHAPETAB:: --loadFile:: could not load '%s': %s - starting empty" % (file_path, e))
            self.failed_load_path = file_path
            self.onNewFile()
            return False
        return True

    def onSaveFile(self, file_name):
        #a load that failed leaves this tab empty while the real data is still on
        #disk - saving now would make that loss permanent
        if self.failed_load_path is not None:
            log.error("CONTROLSHAPETAB:: --onSaveFile:: Not saving: '%s' could not be read earlier, so this tab is "
                      "empty and saving would overwrite the project's real data." % self.failed_load_path)
            return False

        with open(file_name, "w") as file:
            file.write(json.dumps(self.serialize(), indent = 4))
        self.setModified(False)
        return True

    def onNewFile(self):
        self.assignments = {}
        self.pushAssignments()
        self.refresh()
        self.setModified(False)

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            #copies: the live dictionary handed out would change under whoever
            #holds the serialized data the next time an assignment is edited
            ('assignments', {control_id: dict(assignment) for control_id, assignment in self.assignments.items()}),
        ])

    def deserialize(self, data, hashmap = {}, restore_id = True):
        if restore_id: self.id = data['id']
        self.assignments = {str(control_id): assignment
                            for control_id, assignment in data.get('assignments', {}).items()}
        self.pushAssignments()
        self.refresh()
        self.setModified(False)
        return True
