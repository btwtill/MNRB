"""Node pack management, in the Node Editor tab rather than Preferences.

Packs are something you reach for while authoring components, so the entry point
sits next to the node list instead of behind a preferences window.
"""

import os
import re

from PySide6 import QtWidgets #type: ignore
from PySide6.QtCore import Qt, QSize #type: ignore

from MNRB.ROSE_Packs import pack_loader #type: ignore
from MNRB.ROSE_Nodes.node_Editor_conf import ROSE_NODE_CATEGORIES, getNodeCategories #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.packs")

COMPONENT_TEMPLATE = '''from MNRB.ROSE_Nodes.node_Editor_conf import registerNode #type: ignore
from MNRB.ROSE_Nodes.rose_node_base import ROSE_Node, ROSE_NodeProperties #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")


class {class_name}Properties(ROSE_NodeProperties):
    pass


@registerNode("{type_id}")
class {class_name}(ROSE_Node):
    type_id = "{type_id}"
    category = "{category_id}"
    operation_title = "{title}"
    icon = ""
    Node_Properties_Class = {class_name}Properties

    #how many guides this component places - set by what guideBuild() below
    #actually creates, so change it there and here together
    guide_count = 1

    def __init__(self, scene):
        super().__init__(scene,
                         inputs = [["parent_ctrl", SocketTypes.srt, False],
                                   ["parent_def", SocketTypes.deform, False]],
                         outputs = [["{module_stub}", SocketTypes.srt, True],
                                    ["{module_stub}", SocketTypes.deform, True]])

    def guideBuild(self):
        """Create this component's guides. See single_deform_component.py."""
        if not super().guideBuild():
            return False
        return True

    def staticBuild(self):
        """Create the deform joints this component drives."""
        if not super().staticBuild():
            return False
        return True

    def componentBuild(self):
        """Create controls and wire the component's internals.

        Constrain through self.constrain(child, parent) rather than building
        matrix networks by hand - that is what makes the component honour the
        matrix/native constraint flag.
        """
        if not super().componentBuild():
            return False
        return True

    def connectComponent(self):
        """Hook this component up to whatever feeds its input sockets."""
        if not super().connectComponent():
            return False
        return True
'''


def toClassName(name):
    parts = re.split(r"[^0-9a-zA-Z]+", name)
    return "".join(part[:1].upper() + part[1:] for part in parts if part) or "NewComponent"


def toPackId(name):
    """A short namespace from a descriptive label.

    Only the part before the first separator is used: a label reads like
    "My Rig - rig specific", and slugifying the whole of it gives
    "my_rig_rig_specific", which is a poor prefix for every node type in the
    pack. The id wants to be short, since it is what "my_rig.spine" is made of.
    """
    leading = re.split(r"\s[-\u2013:]\s|[(\[:]", name)[0]
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", leading).strip("_").lower()
    cleaned = re.sub(r"_+", "_", cleaned)
    #must start with a letter, since it prefixes an identifier-like id
    return re.sub(r"^[^a-z]+", "", cleaned)


def toModuleName(name):
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()
    return (cleaned or "new_component") + "_component"


def setPathPreview(label, summary, full_path):
    """Short, readable preview text with the full path on hover.

    An absolute path in a form row wraps to several lines and then gets clipped,
    because a word-wrapped QLabel does not report the height it actually needs to
    the form layout. Keeping the visible text to one or two short lines avoids the
    problem rather than fighting the layout for space.
    """
    label.setText(summary)
    label.setToolTip(full_path)

    window = label.window()
    if window is not None:
        window.adjustSize()


class NewPackDialog(QtWidgets.QDialog):
    """Create a pack folder and its manifest, so there is something to add nodes to."""

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("New Node Pack")
        self.setMinimumWidth(560)
        self.created_path = None
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        intro = QtWidgets.QLabel(
            "A pack folder belongs with the rig it is for, not with ROSE, so that anyone "
            "cloning that rig gets its component types automatically.")
        intro.setWordWrap(True)
        layout.addRow(intro)

        location_row = QtWidgets.QHBoxLayout()
        self.location_edit = QtWidgets.QLineEdit()
        self.location_edit.setPlaceholderText("folder the pack will be created in")
        browse_button = QtWidgets.QPushButton("Browse...")
        browse_button.clicked.connect(self.onBrowse)
        location_row.addWidget(self.location_edit)
        location_row.addWidget(browse_button)
        layout.addRow("Location:", location_row)

        self.label_edit = QtWidgets.QLineEdit()
        self.label_edit.setPlaceholderText("My Rig - rig specific")
        layout.addRow("Label:", self.label_edit)

        self.pack_id_edit = QtWidgets.QLineEdit()
        self.pack_id_edit.setPlaceholderText("my_rig")
        layout.addRow("Pack id:", self.pack_id_edit)

        hint = QtWidgets.QLabel(
            "The pack id prefixes every node type it provides (my_rig.spine). It is what "
            "keeps two people's components from colliding, so make it specific to the rig.")
        hint.setWordWrap(True)
        layout.addRow("", hint)

        self.preview_label = QtWidgets.QLabel("")
        self.preview_label.setWordWrap(True)
        self.preview_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addRow("Creates:", self.preview_label)

        self.label_edit.textChanged.connect(self.onLabelChanged)
        self.pack_id_edit.textChanged.connect(self.updatePreview)
        self.location_edit.textChanged.connect(self.updatePreview)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.onCreate)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def onBrowse(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Where should the pack folder go?")
        if folder:
            self.location_edit.setText(folder)

    def onLabelChanged(self, text):
        #only auto-fills while the id has not been typed into
        if not self.pack_id_edit.isModified():
            self.pack_id_edit.setText(toPackId(text))
        self.updatePreview()

    def packFolder(self):
        pack_id = self.pack_id_edit.text().strip()
        location = self.location_edit.text().strip()
        if not pack_id or not location:
            return None
        return os.path.join(location, pack_id + "_nodes")

    def updatePreview(self):
        folder = self.packFolder()

        if not folder:
            setPathPreview(self.preview_label, "", "")
            return

        setPathPreview(self.preview_label,
                       os.path.join(os.path.basename(folder), pack_loader.MANIFEST_NAME),
                       os.path.join(folder, pack_loader.MANIFEST_NAME))

    def onCreate(self):
        import json

        pack_id = self.pack_id_edit.text().strip()
        location = self.location_edit.text().strip()

        if not location or not os.path.isdir(location):
            QtWidgets.QMessageBox.warning(self, "Pick a location", "Choose a folder for the pack.")
            return

        if not re.match(r"^[a-z][a-z0-9_]*$", pack_id):
            QtWidgets.QMessageBox.warning(self, "Invalid pack id",
                                          "A pack id starts with a letter and uses lowercase "
                                          "letters, digits and underscores.\n\nGot: '%s'" % pack_id)
            return

        if pack_id == "rose":
            QtWidgets.QMessageBox.warning(self, "Reserved", "'rose' is the core pack id.")
            return

        if pack_id in pack_loader.LOADED_PACKS:
            QtWidgets.QMessageBox.warning(self, "Already loaded",
                                          "A pack with id '%s' is already loaded from:\n%s"
                                          % (pack_id, pack_loader.LOADED_PACKS[pack_id]["path"]))
            return

        folder = self.packFolder()
        manifest_path = os.path.join(folder, pack_loader.MANIFEST_NAME)

        if os.path.exists(manifest_path):
            QtWidgets.QMessageBox.warning(self, "Already a pack", "%s already exists." % manifest_path)
            return

        os.makedirs(folder, exist_ok = True)

        manifest = {
            "pack_id": pack_id,
            "label": self.label_edit.text().strip() or pack_id,
            "categories": [{"id": "%s.components" % pack_id,
                            "label": self.label_edit.text().strip() or pack_id,
                            "order": 100}],
            "nodes": [],
            "requires_plugins": [],
        }
        with open(manifest_path, "w") as manifest_file:
            json.dump(manifest, manifest_file, indent=4)

        pack_loader.addPackSearchPath(folder)
        try:
            pack_loader.loadPack(folder)
        except Exception as error:
            QtWidgets.QMessageBox.warning(self, "Created, but not loaded",
                                          "Wrote %s but loading it failed:\n\n%s" % (manifest_path, error))

        self.created_path = folder
        self.accept()


class PackManagerDialog(QtWidgets.QDialog):
    """Add, remove and reload node packs."""

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Node Packs")
        self.setMinimumWidth(680)
        self.initUI()
        self.refresh()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        intro = QtWidgets.QLabel(
            "Packs provide rig-specific component types. Where a pack lives is stored per "
            "machine; what it contains travels with the rig in its rose_pack.json.")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self.pack_list = QtWidgets.QListWidget()
        self.pack_list.setWordWrap(True)
        self.pack_list.setMinimumHeight(180)
        layout.addWidget(self.pack_list)

        button_row = QtWidgets.QHBoxLayout()
        new_button = QtWidgets.QPushButton("New Pack...")
        new_button.clicked.connect(self.onNewPack)
        add_button = QtWidgets.QPushButton("Add Existing Pack...")
        add_button.clicked.connect(self.onAddPack)
        remove_button = QtWidgets.QPushButton("Remove Selected")
        remove_button.clicked.connect(self.onRemovePack)
        reload_button = QtWidgets.QPushButton("Reload Packs")
        reload_button.clicked.connect(self.onReloadPacks)

        for button in (new_button, add_button, remove_button, reload_button):
            button_row.addWidget(button)
        button_row.addStretch()
        layout.addLayout(button_row)

        close_button = QtWidgets.QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

    def refresh(self):
        self.pack_list.clear()

        loaded_by_path = {pack["path"]: (pack_id, pack)
                          for pack_id, pack in pack_loader.LOADED_PACKS.items()}

        for path in pack_loader.getPackSearchPaths():
            if path in loaded_by_path:
                pack_id, pack = loaded_by_path[path]
                text = "%s  [%s]  -  %d node type(s)\n      %s" % (
                    pack["label"], pack_id, len(pack["type_ids"]), path)
            elif path in pack_loader.FAILED_PACKS:
                text = "FAILED: %s\n      %s" % (pack_loader.FAILED_PACKS[path], path)
            else:
                text = "not loaded\n      %s" % path

            item = QtWidgets.QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setToolTip(path)
            #two-line rows are clipped without an explicit hint - the widget sizes
            #itself from the first line only
            line_height = self.pack_list.fontMetrics().height()
            item.setSizeHint(QSize(0, line_height * (text.count("\n") + 1) + 8))
            self.pack_list.addItem(item)

    def onNewPack(self):
        dialog = NewPackDialog(self)
        if dialog.exec() and dialog.created_path:
            self.refresh()

    def onAddPack(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder containing rose_pack.json")
        if not folder:
            return

        try:
            pack_loader.readManifest(folder)
        except Exception as error:
            QtWidgets.QMessageBox.warning(self, "Not a node pack",
                                          "%s\n\n%s" % (folder, error))
            return

        pack_loader.addPackSearchPath(folder)
        pack_loader.loadAllPacks()
        self.refresh()

    def onRemovePack(self):
        item = self.pack_list.currentItem()
        if item is None:
            return

        path = item.data(Qt.ItemDataRole.UserRole)
        pack_loader.removePackSearchPath(path)

        #graphs already open keep their nodes; only new loads are affected
        for pack_id, pack in list(pack_loader.LOADED_PACKS.items()):
            if pack["path"] == path:
                pack_loader.unregisterPack(pack_id)

        self.refresh()

    def onReloadPacks(self):
        pack_loader.loadAllPacks()
        self.refresh()


class NewComponentTypeDialog(QtWidgets.QDialog):
    """Scaffold a new component: writes the module and updates the manifest."""

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("New Component Type")
        self.setMinimumWidth(560)
        self.created_type_id = None
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        self.pack_combo = QtWidgets.QComboBox()
        for pack_id, pack in sorted(pack_loader.LOADED_PACKS.items()):
            self.pack_combo.addItem("%s  [%s]" % (pack["label"], pack_id), pack_id)
        layout.addRow("Pack:", self.pack_combo)

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Spine")
        layout.addRow("Name:", self.name_edit)

        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.setEditable(True)
        for category_id, label in getNodeCategories():
            self.category_combo.addItem("%s  [%s]" % (label, category_id), category_id)
        layout.addRow("Category:", self.category_combo)

        self.preview_label = QtWidgets.QLabel("")
        self.preview_label.setWordWrap(True)
        self.preview_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addRow("Creates:", self.preview_label)

        self.name_edit.textChanged.connect(self.updatePreview)
        self.pack_combo.currentIndexChanged.connect(self.onPackChanged)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.onCreate)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if self.pack_combo.count() == 0:
            self.preview_label.setText("No packs loaded. Create one with Node Packs -> New Pack first.")

        self.onPackChanged()

    def selectedPackId(self):
        return self.pack_combo.currentData()

    def onPackChanged(self):
        """Default to the pack's own category rather than a core one.

        Without this every scaffolded component quietly landed in
        rose.base_components, because that is simply the first row.
        """
        pack_id = self.selectedPackId()
        if pack_id:
            for index in range(self.category_combo.count()):
                if str(self.category_combo.itemData(index) or "").startswith(pack_id + "."):
                    self.category_combo.setCurrentIndex(index)
                    break

        self.updatePreview()

    def selectedCategoryId(self):
        typed = self.category_combo.currentText().strip()
        current_index = self.category_combo.currentIndex()

        #currentData() keeps returning the selected row's id even after the text
        #has been typed over, so the row only counts while the text still matches it
        if current_index >= 0 and typed == self.category_combo.itemText(current_index):
            data = self.category_combo.itemData(current_index)
            if data:
                return data

        #typed rather than picked: namespace a new category under the pack, so it
        #cannot collide with another pack's category either
        typed = self.category_combo.currentText().strip()
        if not typed:
            return None
        if "." in typed:
            return typed
        return "%s.%s" % (self.selectedPackId(), re.sub(r"[^0-9a-zA-Z]+", "_", typed).strip("_").lower())

    def updatePreview(self):
        pack_id = self.selectedPackId()
        name = self.name_edit.text().strip()
        if not pack_id or not name:
            return

        pack = pack_loader.LOADED_PACKS.get(pack_id, {})
        module_file = toModuleName(name) + ".py"
        pack_path = pack.get("path", "")
        type_id = "%s.%s" % (pack_id, re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower())

        setPathPreview(self.preview_label,
                       "%s  in  %s\ntype id:  %s" % (module_file, os.path.basename(pack_path) or "?", type_id),
                       os.path.join(pack_path, module_file))

    def onCreate(self):
        import json

        pack_id = self.selectedPackId()
        name = self.name_edit.text().strip()

        if not pack_id or not name:
            QtWidgets.QMessageBox.warning(self, "Missing details", "Pick a pack and enter a name.")
            return

        pack = pack_loader.LOADED_PACKS[pack_id]
        pack_path = pack["path"]
        module_name = toModuleName(name)
        class_name = toClassName(name)
        type_id = "%s.%s" % (pack_id, re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower())
        category_id = self.selectedCategoryId() or "%s.components" % pack_id

        module_path = os.path.join(pack_path, module_name + ".py")
        if os.path.exists(module_path):
            QtWidgets.QMessageBox.warning(self, "Already exists", "%s already exists." % module_path)
            return

        manifest_path = os.path.join(pack_path, pack_loader.MANIFEST_NAME)
        with open(manifest_path, "r") as manifest_file:
            manifest = json.load(manifest_file)

        if any(node.get("type_id") == type_id for node in manifest.get("nodes", [])):
            QtWidgets.QMessageBox.warning(self, "Already exists", "%s is already in this pack." % type_id)
            return

        with open(module_path, "w") as module_file:
            module_file.write(COMPONENT_TEMPLATE.format(
                class_name = class_name, type_id = type_id, category_id = category_id,
                title = name, module_stub = type_id.split(".")[-1]))

        manifest.setdefault("nodes", []).append(
            {"type_id": type_id, "module": module_name, "class": class_name})

        known_categories = {category["id"] for category in manifest.get("categories", [])}
        if category_id not in known_categories and category_id not in ROSE_NODE_CATEGORIES:
            manifest.setdefault("categories", []).append(
                {"id": category_id, "label": name if "." not in self.category_combo.currentText()
                 else category_id, "order": 100})

        with open(manifest_path, "w") as manifest_file:
            json.dump(manifest, manifest_file, indent=4)

        try:
            pack_loader.loadPack(pack_path)
        except Exception as error:
            QtWidgets.QMessageBox.warning(self, "Created, but not loaded",
                                          "Wrote %s but reloading the pack failed:\n\n%s"
                                          % (module_path, error))
            self.created_type_id = type_id
            self.accept()
            return

        self.created_type_id = type_id
        log.debug("PACKS:: created component type '%s' at %s" % (type_id, module_path))
        self.accept()
