from collections import OrderedDict
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox #type: ignore
from MNRB.ROSE_Attributes.attribute_types import AttributeType #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_Node import AttributeGraphNode, AttributeNodeProperties #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_conf import (registerAttributeNode, #type: ignore
                                                                    OPERATIONCODE_ATTRIBUTE_NODE)
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_categories import CATEGORY_SOURCE #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")

class AttributeNodeProperties_Attribute(AttributeNodeProperties):
    """Adds an editor for rig-root attributes.

    A component's attributes are declared in its own initAttributes() and are not
    editable here. A rig-root one is authored in this tab, so it has to be fixable
    here too - otherwise a typo in an enum's options is permanent, there being no
    way to delete a custom attribute either.
    """

    def initUI(self):
        super().initUI()

        self.custom_group_label = QLabel("Rig root attribute")
        self.layout.addWidget(self.custom_group_label)

        self.options_label = QLabel("Enum options (comma separated):")
        self.layout.addWidget(self.options_label)

        self.options_edit = QLineEdit()
        self.options_edit.setPlaceholderText("Option A, Option B")
        self.options_edit.editingFinished.connect(self.onOptionsEdited)
        self.layout.addWidget(self.options_edit)

        #one widget per type rather than a single text field - a bool wants a
        #checkbox and an enum wants its own options, not a number
        self.default_label = QLabel("Default value:")
        self.layout.addWidget(self.default_label)

        self.default_checkbox = QCheckBox("On")
        self.default_checkbox.stateChanged.connect(self.onDefaultEdited)
        self.layout.addWidget(self.default_checkbox)

        self.default_combo = QComboBox()
        self.default_combo.currentIndexChanged.connect(self.onDefaultEdited)
        self.layout.addWidget(self.default_combo)

        self.default_edit = QLineEdit()
        self.default_edit.setPlaceholderText("0")
        self.default_edit.editingFinished.connect(self.onDefaultEdited)
        self.layout.addWidget(self.default_edit)

        self.limits_label = QLabel("Limits (leave empty for none):")
        self.layout.addWidget(self.limits_label)

        self.minimum_edit = QLineEdit()
        self.minimum_edit.setPlaceholderText("minimum")
        self.minimum_edit.editingFinished.connect(self.onLimitsEdited)
        self.layout.addWidget(self.minimum_edit)

        self.maximum_edit = QLineEdit()
        self.maximum_edit.setPlaceholderText("maximum")
        self.maximum_edit.editingFinished.connect(self.onLimitsEdited)
        self.layout.addWidget(self.maximum_edit)

        self.remove_button = QPushButton("Delete this rig attribute")
        self.remove_button.clicked.connect(self.onRemoveCustomAttribute)
        self.layout.addWidget(self.remove_button)

    def getEditableCustomAttribute(self):
        """The attribute behind this node, but only when it is a rig-root one -
        component attributes are declared in code and not editable here."""
        component_attribute = self.node.resolveAttribute()
        if component_attribute is None:
            return None
        if component_attribute.node.getComponentFullPrefix() != "":
            return None
        return component_attribute

    def onOptionsEdited(self):
        component_attribute = self.getEditableCustomAttribute()
        if component_attribute is None:
            return

        options = [option.strip() for option in self.options_edit.text().split(",") if option.strip()]
        if not options:
            self.refresh()
            return

        component_attribute.options = options
        self.setHasBeenModified()

    def onDefaultEdited(self, *args):
        component_attribute = self.getEditableCustomAttribute()
        if component_attribute is None:
            return

        attribute_type = component_attribute.attribute_type

        if attribute_type == AttributeType.BOOL:
            component_attribute.default_value = self.default_checkbox.isChecked()
        elif attribute_type == AttributeType.ENUM:
            component_attribute.default_value = max(self.default_combo.currentIndex(), 0)
        else:
            value = self.parseLimit(self.default_edit.text())
            if value is None:
                value = 0
            component_attribute.default_value = int(value) if attribute_type == AttributeType.INT else value

        self.setHasBeenModified()
        self.refresh()

    def parseLimit(self, text):
        #empty means "no limit", which is not the same as a limit of 0
        text = text.strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    def onLimitsEdited(self):
        component_attribute = self.getEditableCustomAttribute()
        if component_attribute is None:
            return

        minimum = self.parseLimit(self.minimum_edit.text())
        maximum = self.parseLimit(self.maximum_edit.text())

        if minimum is not None and maximum is not None and minimum > maximum:
            log.warning("ATTRIBUTENODE:: minimum %s is above maximum %s - ignored" % (minimum, maximum))
            self.refresh()
            return

        component_attribute.minimum = minimum
        component_attribute.maximum = maximum
        self.setHasBeenModified()
        self.refresh()

    def onRemoveCustomAttribute(self):
        component_attribute = self.getEditableCustomAttribute()
        if component_attribute is None:
            return

        host = component_attribute.node
        host.removeAttribute(component_attribute.id)

        tab = self.node.scene.attribute_tab
        if tab is not None:
            tab.refreshSourceLists()
            tab.setModified(True)

        #the node now points at something that no longer exists - drop it, and its
        #edges with it, rather than leaving a permanently unresolved node behind
        self.node.remove()

    def refresh(self):
        super().refresh()

        if not hasattr(self, "options_edit"):
            return

        component_attribute = self.getEditableCustomAttribute()
        is_custom = component_attribute is not None
        is_enum = is_custom and component_attribute.attribute_type == AttributeType.ENUM
        #only the numeric types can carry limits
        is_numeric = is_custom and component_attribute.attribute_type in (AttributeType.INT,
                                                                          AttributeType.FLOAT)

        self.custom_group_label.setVisible(is_custom)
        self.remove_button.setVisible(is_custom)
        self.options_label.setVisible(is_enum)
        self.options_edit.setVisible(is_enum)
        self.limits_label.setVisible(is_numeric)
        self.minimum_edit.setVisible(is_numeric)
        self.maximum_edit.setVisible(is_numeric)

        self.default_label.setVisible(is_custom)
        self.default_checkbox.setVisible(is_custom and component_attribute.attribute_type == AttributeType.BOOL)
        self.default_combo.setVisible(is_enum)
        self.default_edit.setVisible(is_numeric)

        if is_custom:
            self.showDefaultValue(component_attribute)

        if is_enum:
            self.options_edit.blockSignals(True)
            self.options_edit.setText(", ".join(component_attribute.options))
            self.options_edit.blockSignals(False)

        if is_numeric:
            for edit, value in ((self.minimum_edit, component_attribute.minimum),
                                (self.maximum_edit, component_attribute.maximum)):
                edit.blockSignals(True)
                edit.setText("" if value is None else str(value))
                edit.blockSignals(False)

    def showDefaultValue(self, component_attribute):
        attribute_type = component_attribute.attribute_type
        default_value = component_attribute.default_value

        if attribute_type == AttributeType.BOOL:
            self.default_checkbox.blockSignals(True)
            self.default_checkbox.setChecked(bool(default_value))
            self.default_checkbox.blockSignals(False)
            return

        if attribute_type == AttributeType.ENUM:
            self.default_combo.blockSignals(True)
            self.default_combo.clear()
            self.default_combo.addItems(component_attribute.options)
            if isinstance(default_value, int) and 0 <= default_value < self.default_combo.count():
                self.default_combo.setCurrentIndex(default_value)
            self.default_combo.blockSignals(False)
            return

        self.default_edit.blockSignals(True)
        self.default_edit.setText(str(default_value))
        self.default_edit.blockSignals(False)

@registerAttributeNode(OPERATIONCODE_ATTRIBUTE_NODE)
class AttributeSourceNode(AttributeGraphNode):
    """One exposed attribute, on a component or on the rig root.

    Has both an input and an output, because an attribute can be either end of a
    relationship: driven by something upstream, and driving something downstream.
    That is also where the one hard rule lives - an attribute that is driven must
    not be proxied onto a control, because the incoming connection owns the value
    and the animator's channel would silently refuse input.
    """

    operation_code = OPERATIONCODE_ATTRIBUTE_NODE
    operation_title = "Attribute"
    category = CATEGORY_SOURCE
    Node_Properties_Class = AttributeNodeProperties_Attribute

    def __init__(self, scene):
        super().__init__(scene,
                         inputs = [["driver", SocketTypes.attribute, False]],
                         outputs = [["out", SocketTypes.attribute, True]])

        #{id, name} rather than an object reference - attributes are recreated on
        #every rig build, so this is resolved on demand like everything else
        self.attribute_ref = None

    def setAttributeRef(self, component_attribute):
        #owner_id is what keeps the name fallback honest: without it, resolving a
        #rig-root attribute called Control_Visibility would match the first
        #component that happens to have one
        self.attribute_ref = {"id": component_attribute.id,
                              "name": component_attribute.attribute_name,
                              "owner_id": component_attribute.node.id,
                              "prefix": self.readOwnerPrefix(component_attribute)}
        self.title = component_attribute.attribute_name
        self.properties.refresh()

    def readOwnerPrefix(self, component_attribute):
        #rig-root attributes have no component prefix, so they get a label rather
        #than an empty subtitle
        prefix = component_attribute.node.getComponentFullPrefix()
        return prefix if prefix else "Rig Root"

    def getSubtitle(self):
        return self.attribute_ref.get("prefix", "") if self.attribute_ref else ""

    def getOwnerNodeId(self):
        """The rig node this attribute belongs to - used to spot two graph nodes
        pointing at the same attribute."""
        component_attribute = self.resolveAttribute()
        return component_attribute.node.id if component_attribute is not None else None

    def resolveAttribute(self):
        if self.attribute_ref is None:
            return None

        #by id across both pools first - ids are derived and stable, so this is
        #exact - then by name, but only within the owner this was authored against
        component_attribute = self.scene.findAttributeById(self.attribute_ref["id"])

        if component_attribute is None:
            component_attribute = self.scene.findAttributeByNameInOwner(
                self.attribute_ref.get("owner_id"), self.attribute_ref["name"])

        if component_attribute is not None:
            self.attribute_ref["id"] = component_attribute.id
            self.attribute_ref["name"] = component_attribute.attribute_name
            self.attribute_ref["owner_id"] = component_attribute.node.id
            self.attribute_ref["prefix"] = self.readOwnerPrefix(component_attribute)

        return component_attribute

    def getDescription(self):
        component_attribute = self.resolveAttribute()
        if component_attribute is None:
            return "Unresolved attribute '%s'" % (self.attribute_ref["name"] if self.attribute_ref else "?")

        description = "%s on %s" % (component_attribute.attribute_name, component_attribute.getHostNode())
        if self.drivesItself():
            description += "\n\nDriven by another node pointing at this same attribute - that would be a cycle."
        if self.isDriven():
            description += "\n\nDriven by an upstream node - it cannot also be proxied onto a control."
        return description

    def getOutputPlug(self):
        component_attribute = self.resolveAttribute()
        if component_attribute is None or not component_attribute.exists():
            return None
        return "%s.%s" % (component_attribute.getHostNode(), component_attribute.attribute_name)

    def feedsAControl(self):
        from MNRB.ROSE_UI.attribute_Editor_UI.graph_nodes.control_node import ControlTargetNode #type: ignore
        #compares operation_code rather than isinstance, which breaks across
        #importlib.reload - the same trap the pipeline steps hit
        return any(node.operation_code == ControlTargetNode.operation_code
                   for node in self.getDownstreamNodes(0))

    def drivesItself(self):
        #the same attribute can legitimately be dragged onto the canvas twice, and
        #wiring one copy into the other would ask Maya to connect a plug to itself -
        #a cycle error at build time rather than anything visible here
        upstream = self.getUpstreamNode(0)
        if upstream is None or not hasattr(upstream, "attribute_ref"):
            return False
        if upstream.attribute_ref is None or self.attribute_ref is None:
            return False
        return upstream.attribute_ref["id"] == self.attribute_ref["id"]

    def isDeprecated(self):
        #a renamed component still resolves - its id is derived from the node and
        #the slot name, neither of which a rename touches - so only a genuinely
        #deleted attribute lands here
        return self.attribute_ref is not None and self.resolveAttribute() is None

    def validate(self):
        is_valid = True

        if self.attribute_ref is None or self.isDeprecated():
            is_valid = False
        elif self.drivesItself():
            is_valid = False
        elif self.isDriven() and self.feedsAControl():
            #the rule the whole graph exists to make visible
            is_valid = False

        return self.setValidity(is_valid)

    def buildDrivingConnections(self):
        """Connect whatever drives this attribute into it. Runs after every node
        has created its Maya nodes, so the upstream plug resolves."""
        upstream = self.getUpstreamNode(0)
        if upstream is None:
            return True, ""

        if self.drivesItself():
            return False, "'%s' is wired to itself" % self.title

        source_plug = upstream.getOutputPlug()
        target_plug = self.getOutputPlug()

        if source_plug is None:
            return False, "'%s' has nothing to read from" % self.title
        if target_plug is None:
            return False, "'%s' is not built in the scene" % self.title

        from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
        source_node, source_attribute = source_plug.split(".", 1)
        target_node, target_attribute = target_plug.split(".", 1)

        #force, so a rebuild replaces the previous driver instead of erroring on
        #an attribute that already has an incoming connection
        MC.connectAttribute(source_node, source_attribute, target_node, target_attribute, force = True)
        return True, ""

    def serialize(self):
        result_data = super().serialize()
        result_data['attribute_ref'] = self.attribute_ref
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id = True, exists = False):
        result = super().deserialize(data, hashmap, restore_id, exists)
        self.attribute_ref = data.get('attribute_ref', None)
        return result
