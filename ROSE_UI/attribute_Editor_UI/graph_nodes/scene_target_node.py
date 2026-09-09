from PySide6.QtWidgets import QLabel, QLineEdit #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_Node import AttributeGraphNode, AttributeNodeProperties #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_conf import (registerAttributeNode, #type: ignore
                                                                    OPERATIONCODE_SCENE_TARGET_NODE)
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_categories import CATEGORY_TARGET #type: ignore
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")

class SceneTargetNodeProperties(AttributeNodeProperties):

    def initUI(self):
        super().initUI()

        self.layout.addWidget(QLabel("Target plug:"))

        self.target_plug_edit = QLineEdit()
        self.target_plug_edit.setPlaceholderText("node.attribute")
        self.target_plug_edit.editingFinished.connect(self.onTargetPlugEdited)
        self.layout.addWidget(self.target_plug_edit)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.layout.addWidget(self.status_label)

    def onTargetPlugEdited(self):
        self.node.target_plug = self.target_plug_edit.text().strip()
        self.node.title = self.node.target_plug if self.node.target_plug else "Scene Target"
        self.node.validate()
        self.setHasBeenModified()

    def refresh(self):
        super().refresh()

        if not hasattr(self, "target_plug_edit"):
            return

        self.target_plug_edit.blockSignals(True)
        self.target_plug_edit.setText(self.node.target_plug)
        self.target_plug_edit.blockSignals(False)

        self.status_label.setText(self.node.getPlugStatus())


@registerAttributeNode(OPERATIONCODE_SCENE_TARGET_NODE)
class SceneTargetNode(AttributeGraphNode):
    """Connects whatever feeds it into an arbitrary plug in the Maya scene.

    Rig-root attributes had nowhere to go: they exist on the rig root but nothing
    said what they should drive. This is that missing half - type the destination
    plug (`node.attribute`) and whatever is wired in drives it.

    Deliberately a plain string rather than a picker: the target usually doesn't
    exist yet when the graph is authored, and it may be created by a later build
    step. The plug is checked at build time and reported if it isn't there.
    """

    operation_code = OPERATIONCODE_SCENE_TARGET_NODE
    operation_title = "Scene Target"
    category = CATEGORY_TARGET
    Node_Properties_Class = SceneTargetNodeProperties

    def __init__(self, scene):
        super().__init__(scene,
                         inputs = [["in", SocketTypes.attribute, False]],
                         outputs = [])
        self.target_plug = ""

    def getSubtitle(self):
        return "scene plug"

    def getDescription(self):
        if not self.target_plug:
            return "Type the plug this should drive, as node.attribute."
        return "Drives %s" % self.target_plug

    def getPlugStatus(self):
        if not self.target_plug:
            return ""
        if "." not in self.target_plug:
            return "Not a plug - expected node.attribute"

        node_name, attribute_name = self.target_plug.split(".", 1)
        if not MC.objectExists(node_name):
            return "'%s' is not in the scene yet" % node_name
        if not MC.attributeExists(node_name, attribute_name):
            return "'%s' has no attribute '%s'" % (node_name, attribute_name)
        return "Resolves to %s" % self.target_plug

    def validate(self):
        #only the things knowable while authoring: something feeding it, and a
        #plausibly-shaped plug. Whether the plug exists is a build-time question.
        is_valid = bool(self.target_plug) and "." in self.target_plug and self.getUpstreamNode(0) is not None
        return self.setValidity(is_valid)

    def buildDrivingConnections(self):
        upstream = self.getUpstreamNode(0)
        if upstream is None:
            return True, ""

        if not self.target_plug or "." not in self.target_plug:
            return False, "Scene Target has no valid target plug"

        node_name, attribute_name = self.target_plug.split(".", 1)
        if not MC.objectExists(node_name):
            return False, "Scene target '%s' is not in the scene" % node_name
        if not MC.attributeExists(node_name, attribute_name):
            return False, "'%s' has no attribute '%s'" % (node_name, attribute_name)

        source_plug = upstream.getOutputPlug()
        if source_plug is None:
            return False, "Nothing to read from for '%s'" % self.target_plug

        source_node, source_attribute = source_plug.split(".", 1)
        MC.connectAttribute(source_node, source_attribute, node_name, attribute_name, force = True)
        return True, ""

    def serialize(self):
        result_data = super().serialize()
        result_data['target_plug'] = self.target_plug
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id = True, exists = False):
        result = super().deserialize(data, hashmap, restore_id, exists)
        self.target_plug = data.get('target_plug', "")
        return result
