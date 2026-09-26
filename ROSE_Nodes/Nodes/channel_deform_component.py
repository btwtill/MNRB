from PySide6.QtWidgets import QGridLayout, QLabel, QCheckBox #type: ignore
from PySide6.QtCore import Qt #type: ignore

from MNRB.ROSE_Nodes.node_Editor_conf import TYPEID_CHANNELDEFORMCOMPONENT, registerNode #type: ignore
from MNRB.ROSE_Nodes.Nodes.single_deform_component import (ROSE_Node_SingleDeformComponent, #type: ignore
                                                           ROSE_Node_SingleDeformComponent_Properties)
from MNRB.ROSE_Constraints.constraint_types import ConstraintChannels #type: ignore


class ROSE_Node_ChannelDeformComponent_Properties(ROSE_Node_SingleDeformComponent_Properties):

    def __init__(self, node):
        #set before super(), which calls initUI() and then reads this back
        self.constraint_channels = ConstraintChannels()
        self.channel_checkboxes = {}
        super().__init__(node)

    def initUI(self):
        super().initUI()

        self.layout.addWidget(QLabel("Deform Constraint Channels:"))

        #translate / rotate / scale down the side, X Y Z across the top
        channel_grid = QGridLayout()
        for column, axis in enumerate(ConstraintChannels.AXES, start = 1):
            channel_grid.addWidget(QLabel(axis), 0, column, alignment = Qt.AlignCenter)

        for row, channel in enumerate(ConstraintChannels.CHANNELS, start = 1):
            channel_grid.addWidget(QLabel(channel.capitalize()), row, 0)

            for column, axis in enumerate(ConstraintChannels.AXES, start = 1):
                checkbox = QCheckBox()
                checkbox.setChecked(self.constraint_channels.isEnabled(channel, axis))
                checkbox.toggled.connect(
                    lambda checked, channel = channel, axis = axis:
                        self.updateConstraintChannel(channel, axis, checked))
                channel_grid.addWidget(checkbox, row, column, alignment = Qt.AlignCenter)
                self.channel_checkboxes[(channel, axis)] = checkbox

        self.layout.addLayout(channel_grid)

    def updateConstraintChannel(self, channel, axis, checked):
        if self.constraint_channels.isEnabled(channel, axis) == checked:
            return

        self.constraint_channels.setEnabled(channel, axis, checked)

        #the constraint is made at connect time, so the built rig keeps the old
        #channels until it is rebuilt
        self.setNeedsRebuild(True, "Deform constraint channels changed")
        self.setHasBeenModified()

    def syncChannelCheckboxes(self):
        for (channel, axis), checkbox in self.channel_checkboxes.items():
            checkbox.setChecked(self.constraint_channels.isEnabled(channel, axis))

    def serialize(self):
        result_data = super().serialize()
        result_data["constraint_channels"] = self.constraint_channels.serialize()
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id = True):
        result = super().deserialize(data, hashmap, restore_id)

        self.constraint_channels = ConstraintChannels.deserialize(data.get("constraint_channels"))

        self.is_silent = True
        self.syncChannelCheckboxes()
        self.is_silent = False

        return result


@registerNode(TYPEID_CHANNELDEFORMCOMPONENT)
class ROSE_Node_ChannelDeformComponent(ROSE_Node_SingleDeformComponent):
    #A single deform whose joint follows its control on chosen axes only - only
    #translate, only rotate X, translate X and Y, and so on. Axes switched off
    #keep the joint's own value. Everything else is the single deform as is.

    type_id = TYPEID_CHANNELDEFORMCOMPONENT
    category = "rose.base_components"
    operation_title = "Channel_Def"
    icon = ""

    Node_Properties_Class = ROSE_Node_ChannelDeformComponent_Properties

    def constrainDeformJoint(self, deform_joint_name):
        return self.constrainDeform(deform_joint_name, self.deform_output, maintain_offset = False,
                                    channels = self.properties.constraint_channels)
