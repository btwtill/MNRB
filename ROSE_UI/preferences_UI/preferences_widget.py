from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QPushButton, QCheckBox, QFrame, QDoubleSpinBox #type: ignore
from PySide6.QtCore import Qt #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore
from MNRB.ROSE_Debug.rose_log_channels import ROSE_LOG_CHANNELS #type: ignore
from MNRB.ROSE_Constraints.constraint_preferences import (isDeformConnectionNative, #type: ignore
                                                          setDeformConnectionNative)
from MNRB.ROSE_Guides.guide_preferences import (getConnectorThicknessMultiplier, #type: ignore
                                                setConnectorThicknessMultiplier,
                                                getConnectorThicknessOverride,
                                                setConnectorThicknessOverride)

CHANNEL_ROLE = Qt.ItemDataRole.UserRole

class ROSEPreferences(QWidget):
    """Preferences window. Currently one page: which log channels are switched on.

    The tree is built from ROSE_LOG_CHANNELS, nested by the dots in the channel
    names, so adding a channel there is enough for it to appear here.
    """

    def __init__(self, on_channels_changed = None):
        super().__init__()

        #let the owner persist the change - this widget deliberately knows nothing
        #about QSettings or where preferences are stored
        self.on_channels_changed = on_channels_changed
        self.items_by_channel = {}
        self.is_applying = False

        self.initUI()

    def initUI(self):
        self.setWindowTitle("ROSE Preferences")
        self.setGeometry(150, 150, 380, 480)

        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel("Debug Logging"))
        self.layout.addWidget(QLabel("Switching a branch on covers everything under it. "
                                     "Warnings and errors are always shown."))

        self.channel_tree = QTreeWidget()
        self.channel_tree.setHeaderHidden(True)
        self.channel_tree.itemChanged.connect(self.onItemChanged)
        self.layout.addWidget(self.channel_tree)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        self.layout.addWidget(separator)

        self.layout.addWidget(QLabel("Rig Building"))

        self.native_deform_checkbox = QCheckBox("Drive deform joints with native Maya constraints")
        self.native_deform_checkbox.setChecked(isDeformConnectionNative())
        self.native_deform_checkbox.stateChanged.connect(self.onNativeDeformChanged)
        self.layout.addWidget(self.native_deform_checkbox)

        native_deform_hint = QLabel(
            "Overrides every component's own constraint type, but only for the connections "
            "that drive deform joints. A matrix network is cheaper and keeps the channel box "
            "clean; native constraints are what survives baking the skeleton out to another "
            "application. Takes effect on the next build.")
        native_deform_hint.setWordWrap(True)
        self.layout.addWidget(native_deform_hint)

        self.layout.addWidget(QLabel("Guide Connectors"))

        multiplier_row = QHBoxLayout()
        multiplier_row.addWidget(QLabel("Thickness x distance:"))
        self.connector_multiplier_spinbox = QDoubleSpinBox()
        self.connector_multiplier_spinbox.setDecimals(4)
        self.connector_multiplier_spinbox.setMinimum(0.0001)
        self.connector_multiplier_spinbox.setMaximum(10.0)
        self.connector_multiplier_spinbox.setSingleStep(0.01)
        self.connector_multiplier_spinbox.setValue(getConnectorThicknessMultiplier())
        self.connector_multiplier_spinbox.valueChanged.connect(setConnectorThicknessMultiplier)
        multiplier_row.addWidget(self.connector_multiplier_spinbox)
        self.layout.addLayout(multiplier_row)

        override_row = QHBoxLayout()
        override_row.addWidget(QLabel("Fixed thickness (0 = off):"))
        self.connector_override_spinbox = QDoubleSpinBox()
        self.connector_override_spinbox.setDecimals(4)
        self.connector_override_spinbox.setMinimum(0.0)
        self.connector_override_spinbox.setMaximum(1000.0)
        self.connector_override_spinbox.setSingleStep(0.1)
        self.connector_override_spinbox.setValue(getConnectorThicknessOverride())
        self.connector_override_spinbox.valueChanged.connect(setConnectorThicknessOverride)
        override_row.addWidget(self.connector_override_spinbox)
        self.layout.addLayout(override_row)

        connector_hint = QLabel("Connector thickness is a fraction of the distance between the two "
                                "guides it joins. Set a fixed thickness to ignore that distance "
                                "entirely. Takes effect the next time guides are built.")
        connector_hint.setWordWrap(True)
        self.layout.addWidget(connector_hint)

        button_row = QHBoxLayout()

        self.enable_all_button = QPushButton("Enable All")
        self.enable_all_button.clicked.connect(self.onEnableAll)
        button_row.addWidget(self.enable_all_button)

        self.disable_all_button = QPushButton("Disable All")
        self.disable_all_button.clicked.connect(self.onDisableAll)
        button_row.addWidget(self.disable_all_button)

        button_row.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_row.addWidget(self.close_button)

        self.layout.addLayout(button_row)
        self.setLayout(self.layout)

        self.buildChannelTree()
        self.showCurrentChannelState()

    def buildChannelTree(self):
        #every setCheckState below emits itemChanged, and without this guard those
        #read as the user unticking all 28 channels - which wrote an empty set
        #straight back over whatever was actually enabled, just by opening the window
        self.is_applying = True

        for channel, label in ROSE_LOG_CHANNELS:
            parent_channel = channel.rsplit(".", 1)[0] if "." in channel else None
            parent_item = self.items_by_channel.get(parent_channel)

            item = QTreeWidgetItem(parent_item) if parent_item is not None else QTreeWidgetItem(self.channel_tree)
            item.setText(0, label)
            item.setData(0, CHANNEL_ROLE, channel)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Unchecked)

            self.items_by_channel[channel] = item

        self.is_applying = False
        self.channel_tree.expandAll()

    def showCurrentChannelState(self):
        enabled_channels = set(ROSE_Log.getEnabledChannels())

        #is_applying suppresses itemChanged while writing state in, so restoring
        #the display doesn't read as the user ticking every box
        self.is_applying = True
        for channel, item in self.items_by_channel.items():
            item.setCheckState(0, Qt.CheckState.Checked if channel in enabled_channels else Qt.CheckState.Unchecked)
        self.is_applying = False

        self.refreshParentCheckStates()

    def onNativeDeformChanged(self, state):
        setDeformConnectionNative(self.native_deform_checkbox.isChecked())

    def onItemChanged(self, item, column):
        if self.is_applying:
            return

        self.is_applying = True
        self.setSubtreeCheckState(item, item.checkState(0))
        self.is_applying = False

        self.refreshParentCheckStates()
        self.applyChannelState()

    def setSubtreeCheckState(self, item, check_state):
        #ticking a branch ticks everything under it, so the stored set always says
        #exactly which channels are on - the logger's "a parent covers its
        #children" rule then agrees with what the tree shows rather than
        #contradicting an unticked child
        for index in range(item.childCount()):
            child = item.child(index)
            child.setCheckState(0, check_state)
            self.setSubtreeCheckState(child, check_state)

    def refreshParentCheckStates(self):
        self.is_applying = True
        for index in range(self.channel_tree.topLevelItemCount()):
            self.refreshParentCheckState(self.channel_tree.topLevelItem(index))
        self.is_applying = False

    def refreshParentCheckState(self, item):
        if item.childCount() == 0:
            return item.checkState(0) == Qt.CheckState.Checked

        children_all_checked = True
        for index in range(item.childCount()):
            if not self.refreshParentCheckState(item.child(index)):
                children_all_checked = False

        #a branch only counts as on when every channel under it is - otherwise it
        #shows partially checked and stays out of the enabled set
        if item.checkState(0) == Qt.CheckState.Checked and not children_all_checked:
            item.setCheckState(0, Qt.CheckState.PartiallyChecked)

        return item.checkState(0) == Qt.CheckState.Checked

    def getCheckedChannels(self):
        return [channel for channel, item in self.items_by_channel.items()
                if item.checkState(0) == Qt.CheckState.Checked]

    def applyChannelState(self):
        ROSE_Log.setEnabledChannels(self.getCheckedChannels())
        if self.on_channels_changed is not None:
            self.on_channels_changed()

    def onEnableAll(self):
        self.setAllChannels(Qt.CheckState.Checked)

    def onDisableAll(self):
        self.setAllChannels(Qt.CheckState.Unchecked)

    def setAllChannels(self, check_state):
        self.is_applying = True
        for item in self.items_by_channel.values():
            item.setCheckState(0, check_state)
        self.is_applying = False

        self.applyChannelState()
