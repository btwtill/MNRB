from PySide6.QtWidgets import (QGridLayout, QLabel, QCheckBox, QGroupBox, QVBoxLayout, QHBoxLayout, #type: ignore
                               QLineEdit, QPushButton, QWidget)
from PySide6.QtCore import Qt #type: ignore

from MNRB.ROSE_Nodes.node_Editor_conf import TYPEID_CHANNELDEFORMCOMPONENT, registerNode #type: ignore
from MNRB.ROSE_Nodes.Nodes.single_deform_component import (ROSE_Node_SingleDeformComponent, #type: ignore
                                                           ROSE_Node_SingleDeformComponent_Properties)
from MNRB.ROSE_Constraints.constraint_types import ConstraintChannels #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.ROSE_Deform.deform import deform #type: ignore
from MNRB.ROSE_naming.ROSE_names import ROSE_Names #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")

#the main joint's name, and so its output socket's - see the single deform
MAIN_DEFORM_NAME = "singleDef"
#a new extra deform follows everything but the rotation
DEFAULT_EXTRA_CHANNELS = {"translate": "XYZ", "rotate": "", "scale": "XYZ"}


def toIdentifier(text, fallback):
    cleaned = "".join(character if character.isalnum() else "_" for character in (text or "")).strip("_")
    if not cleaned:
        return fallback
    return cleaned if cleaned[0].isalpha() else "d" + cleaned


class ROSE_Node_ChannelDeformComponent_Properties(ROSE_Node_SingleDeformComponent_Properties):

    def __init__(self, node):
        #set before super(), which calls initUI() and then reads this back
        self.constraint_channels = ConstraintChannels()
        self.channel_checkboxes = {}
        #more joints following the same control, each on its own channels -
        #[{"name", "channels": {"translate", "rotate", "scale"}}]
        self.extra_deforms = []
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

        self.layout.addWidget(QLabel("Extra Deforms - more joints on the same control, each with its own channels:"))
        self.extras_widget = QWidget()
        self.extras_layout = QVBoxLayout(self.extras_widget)
        self.extras_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.extras_widget)
        self.add_extra_button = QPushButton("Add Deform")
        self.add_extra_button.setToolTip("Another joint following this control - by default on everything but "
                                         "the rotation. It gets its own srt and deform outputs")
        self.add_extra_button.clicked.connect(self.onAddExtraDeform)
        self.layout.addWidget(self.add_extra_button)
        self.rebuildExtraRows()

    def buildChannelGrid(self, channels, on_toggle):
        grid = QGridLayout()
        for column, axis in enumerate(ConstraintChannels.AXES, start = 1):
            grid.addWidget(QLabel(axis), 0, column, alignment = Qt.AlignCenter)
        for row, channel in enumerate(ConstraintChannels.CHANNELS, start = 1):
            grid.addWidget(QLabel(channel.capitalize()), row, 0)
            for column, axis in enumerate(ConstraintChannels.AXES, start = 1):
                checkbox = QCheckBox()
                checkbox.setChecked(channels.isEnabled(channel, axis))
                checkbox.toggled.connect(lambda checked, channel = channel, axis = axis: on_toggle(channel, axis, checked))
                grid.addWidget(checkbox, row, column, alignment = Qt.AlignCenter)
        return grid

    def rebuildExtraRows(self):
        while self.extras_layout.count():
            item = self.extras_layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
        for index, extra in enumerate(self.extra_deforms):
            box = QGroupBox()
            box_layout = QVBoxLayout(box)
            header = QHBoxLayout()
            name_edit = QLineEdit(extra["name"])
            name_edit.setToolTip("The joint's name - and its output sockets'")
            name_edit.editingFinished.connect(lambda index = index, edit = name_edit: self.onRenameExtraDeform(index, edit))
            header.addWidget(QLabel("Name:"))
            header.addWidget(name_edit, 1)
            remove = QPushButton("Remove")
            remove.clicked.connect(lambda checked = False, index = index: self.onRemoveExtraDeform(index))
            header.addWidget(remove)
            box_layout.addLayout(header)
            channels = ConstraintChannels.deserialize(extra["channels"])
            box_layout.addLayout(self.buildChannelGrid(
                channels, lambda channel, axis, checked, index = index: self.updateExtraChannel(index, channel, axis, checked)))
            self.extras_layout.addWidget(box)

    def uniqueExtraName(self, wanted, skip_index = None):
        taken = {MAIN_DEFORM_NAME} | {extra["name"] for index, extra in enumerate(self.extra_deforms) if index != skip_index}
        name, number = wanted, 1
        while name in taken:
            name = "%s%d" % (wanted, number)
            number += 1
        return name

    def onAddExtraDeform(self):
        name = self.uniqueExtraName("noRotation")
        self.extra_deforms.append({"name": name, "channels": dict(DEFAULT_EXTRA_CHANNELS)})
        self.node.addOutputSocket(SocketTypes.srt, name, True)
        self.node.addOutputSocket(SocketTypes.deform, name, True)
        self.rebuildExtraRows()
        self.setNeedsRebuild(True, "Extra deforms changed")
        self.setHasBeenModified()

    def onRemoveExtraDeform(self, index):
        srt_socket, deform_socket = self.node.getExtraSrtSocket(index), self.node.getExtraDeformSocket(index)
        self.node.removeOutputSocket(deform_socket)
        self.node.removeOutputSocket(srt_socket)
        del self.extra_deforms[index]
        self.rebuildExtraRows()
        self.setNeedsRebuild(True, "Extra deforms changed")
        self.setHasBeenModified()

    def onRenameExtraDeform(self, index, edit):
        name = self.uniqueExtraName(toIdentifier(edit.text(), "extraDef"), skip_index = index)
        edit.setText(name)
        if name == self.extra_deforms[index]["name"]:
            return
        self.extra_deforms[index]["name"] = name
        #renamed in place: an edge out of them stays connected
        self.node.renameOutputSocket(self.node.getExtraSrtSocket(index), name)
        self.node.renameOutputSocket(self.node.getExtraDeformSocket(index), name)
        self.setNeedsRebuild(True, "Extra deform renamed")
        self.setHasBeenModified()

    def updateExtraChannel(self, index, channel, axis, checked):
        channels = ConstraintChannels.deserialize(self.extra_deforms[index]["channels"])
        if channels.isEnabled(channel, axis) == checked:
            return
        channels.setEnabled(channel, axis, checked)
        self.extra_deforms[index]["channels"] = channels.serialize()
        self.setNeedsRebuild(True, "Deform constraint channels changed")
        self.setHasBeenModified()

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
        result_data["extra_deforms"] = [dict(name = e["name"], channels = dict(e["channels"])) for e in self.extra_deforms]
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id = True):
        result = super().deserialize(data, hashmap, restore_id)

        self.constraint_channels = ConstraintChannels.deserialize(data.get("constraint_channels"))
        #their output sockets were already restored with the node's - only the list here
        self.extra_deforms = [dict(name = e["name"], channels = dict(e["channels"])) for e in data.get("extra_deforms", [])]

        self.is_silent = True
        self.syncChannelCheckboxes()
        self.rebuildExtraRows()
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

    #Extra deforms: more joints following the same control, each on its own
    #channels - the full motion on the main joint and the same without the
    #rotation on another, say. Each sits beside the main joint, not under it, so
    #it inherits nothing from it. Each has an srt output and a deform output of
    #its own, named after it: the srt output is the control's motion on the
    #extra's channels only, and the extra joint follows that output.

    def constrainDeformJoint(self, deform_joint_name):
        return self.constrainDeform(deform_joint_name, self.deform_output, maintain_offset = False,
                                    channels = self.properties.constraint_channels)

    def getExtraSrtSocket(self, index):
        #after the main joint's srt and deform outputs, an srt and a deform per
        #extra, in the extras' order
        return self.outputs[2 + 2 * index]

    def getExtraDeformSocket(self, index):
        return self.outputs[3 + 2 * index]

    def deserialize(self, data, hashmap = {}, restore_id = True, exists = False):
        result = super().deserialize(data, hashmap, restore_id, exists)
        self.addMissingExtraSrtSockets()
        return result

    def addMissingExtraSrtSockets(self):
        #projects saved before the extras had srt outputs hold only a deform
        #socket per extra. The srt socket goes in before it; the deform socket
        #keeps its id, so its edges stay
        for index, extra in enumerate(self.properties.extra_deforms):
            position = 2 + 2 * index
            if position < len(self.outputs) and self.outputs[position].socket_type == SocketTypes.srt:
                continue
            self.insertOutputSocket(position, SocketTypes.srt, extra["name"], True)

    def getExtraDeform(self, name):
        for component_deform in self.deforms:
            if component_deform.deform_name == name:
                return component_deform
        return None

    def staticBuild(self):
        if not super().staticBuild():
            return False
        position = self.guides[0].getPosition()
        for extra in self.properties.extra_deforms:
            extra_deform = deform(self, extra["name"])
            MC.setJointPositionMatrix(extra_deform.name, position)
            MC.parentObject(extra_deform.name, self.scene.virtual_rig_hierarchy.skeleton_hierarchy_object.name)
        return True

    def connectInputs(self):
        connected = super().connectInputs()
        #the extras hang where the main joint hangs - beside it, never under it
        if self.isInputSocketConnected(1):
            deform_parent = self.getInputConnectionValueAt(1)
            for extra in self.properties.extra_deforms:
                extra_deform = self.getExtraDeform(extra["name"])
                if extra_deform is not None:
                    MC.parentObject(extra_deform.name, deform_parent + ROSE_Names.deform_suffix)
        return connected

    def componentBuild(self):
        if not super().componentBuild():
            return False
        for extra in self.properties.extra_deforms:
            self.buildExtraOutput(extra)
        return True

    def buildExtraOutput(self, extra):
        #the control's motion on the extra's channels only: the output lives in
        #the control's parent space and takes just the enabled channels from it,
        #the others staying at rest
        prefix = self.getComponentFullPrefix()
        output = MC.createTransform(prefix + extra["name"] + ROSE_Names.output_suffix)
        MC.parentObject(output, self.output_hierarchy)
        local_matrix = self.trackBuiltNode(MC.createMultMatrixNode(prefix + extra["name"] + "OutputLocal"))
        MC.connectAttribute(self.single_control.name, "parentMatrix[0]", local_matrix, "matrixIn[0]")
        MC.connectAttribute(self.output_hierarchy, "worldInverseMatrix[0]", local_matrix, "matrixIn[1]")
        MC.connectAttribute(local_matrix, "matrixSum", output, "offsetParentMatrix", force = True)
        MC.connectAttribute(self.single_control.name, "rotateOrder", output, "rotateOrder")
        channels = ConstraintChannels.deserialize(extra["channels"])
        for channel in ConstraintChannels.CHANNELS:
            for axis in ConstraintChannels.AXES:
                if channels.isEnabled(channel, axis):
                    MC.connectAttribute(self.single_control.name, channel + axis, output, channel + axis)
        return output

    def connectDeforms(self):
        super().connectDeforms()
        for extra in self.properties.extra_deforms:
            extra_deform = self.getExtraDeform(extra["name"])
            if extra_deform is None:
                log.warning("%s:: --connectDeforms:: no '%s' joint - run the static build to add it"
                            % (self.__class__.__name__, extra["name"]))
                continue
            MC.resetJointOrientations(extra_deform.name)
            #the channels are already picked in its srt output
            self.constrainDeform(extra_deform.name, self.getComponentFullPrefix() + extra["name"] + ROSE_Names.output_suffix,
                                 maintain_offset = False)
        return True
