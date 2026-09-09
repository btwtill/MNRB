from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLineEdit, QComboBox, #type: ignore
                               QLabel, QSizePolicy)
from MNRB.ROSE_Attributes.attribute_types import AttributeType #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")

def parseEnumOptions(text):
    """Comma separated in, ordered list out. Maya joins them with colons itself,
    so a colon-separated string is accepted too."""
    separator = ":" if ":" in text and "," not in text else ","
    return [option.strip() for option in text.split(separator) if option.strip()]

class AttributeEditorToolbar(QWidget):
    """Build actions, plus creating a custom attribute that belongs to the rig
    rather than to any component."""

    def __init__(self, tab, parent = None):
        super().__init__(parent)

        self.tab = tab
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.build_all_button = QPushButton("Build Graph")
        self.build_all_button.setToolTip(
            "Create the operator nodes, wire the driving connections, then proxy "
            "onto every control - in that order")
        self.build_all_button.clicked.connect(self.tab.onBuildAll)
        self.layout.addWidget(self.build_all_button)

        self.remove_deprecated_button = QPushButton("Remove Deprecated")
        self.remove_deprecated_button.setToolTip(
            "Delete every node whose attribute or control no longer exists in the rig, "
            "along with the edges into it")
        self.remove_deprecated_button.clicked.connect(self.tab.onRemoveDeprecated)
        self.layout.addWidget(self.remove_deprecated_button)

        self.layout.addSpacing(20)
        self.layout.addWidget(QLabel("New rig attribute:"))

        self.custom_name_edit = QLineEdit()
        self.custom_name_edit.setPlaceholderText("Attribute name")
        self.custom_name_edit.setMaximumWidth(160)
        self.layout.addWidget(self.custom_name_edit)

        self.custom_type_combo = QComboBox()
        for attribute_type in AttributeType:
            self.custom_type_combo.addItem(attribute_type.value, attribute_type)
        self.custom_type_combo.currentIndexChanged.connect(self.updateEnumOptionsVisibility)
        self.layout.addWidget(self.custom_type_combo)

        #an enum is useless without its options, and there was no way to give them
        self.custom_options_edit = QLineEdit()
        self.custom_options_edit.setPlaceholderText("Option A, Option B, Option C")
        self.custom_options_edit.setMaximumWidth(220)
        self.custom_options_edit.setToolTip("Comma separated, in channel-box order")
        self.layout.addWidget(self.custom_options_edit)

        self.add_custom_button = QPushButton("Add")
        self.add_custom_button.clicked.connect(self.onAddCustomAttribute)
        self.layout.addWidget(self.add_custom_button)

        self.layout.addStretch()

        self.updateEnumOptionsVisibility()

    def updateEnumOptionsVisibility(self):
        self.custom_options_edit.setVisible(self.custom_type_combo.currentData() == AttributeType.ENUM)

    def onAddCustomAttribute(self):
        name = self.custom_name_edit.text().strip()
        if not name:
            return

        attribute_type = self.custom_type_combo.currentData()
        options = parseEnumOptions(self.custom_options_edit.text()) if attribute_type == AttributeType.ENUM else None

        if attribute_type == AttributeType.ENUM and not options:
            log.warning("ATTRIBUTEEDITORTOOLBAR:: an enum attribute needs at least one option")
            return

        if self.tab.addCustomAttribute(name, attribute_type, options):
            self.custom_name_edit.clear()
            self.custom_options_edit.clear()

    def setRemoveDeprecatedEnabled(self, is_enabled):
        self.remove_deprecated_button.setEnabled(is_enabled)
