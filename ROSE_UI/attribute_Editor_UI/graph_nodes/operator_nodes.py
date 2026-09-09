from PySide6.QtWidgets import QLabel, QDoubleSpinBox, QComboBox #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_Node import AttributeGraphNode, AttributeNodeProperties #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_conf import (registerAttributeNode, #type: ignore
                                                                    OPERATIONCODE_REVERSE_NODE,
                                                                    OPERATIONCODE_MULTIPLY_NODE,
                                                                    OPERATIONCODE_CONDITION_NODE,
                                                                    OPERATIONCODE_CLAMP_NODE)
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.ROSE_UI.attribute_Editor_UI.attribute_Editor_categories import CATEGORY_OPERATOR #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.components")

def buildSpinBox(minimum, maximum, value, on_changed):
    spin_box = QDoubleSpinBox()
    spin_box.setRange(minimum, maximum)
    spin_box.setDecimals(3)
    spin_box.setValue(value)
    spin_box.valueChanged.connect(on_changed)
    return spin_box


class OperatorNode(AttributeGraphNode):
    """Shared behaviour for the utility-node operators.

    Each becomes one or more native Maya utility nodes at build time, so the
    common driven-attribute plumbing - invert a visibility, scale a value, switch
    on a comparison - doesn't have to be hand-wired outside ROSE.
    """

    category = CATEGORY_OPERATOR
    output_attribute = "output"

    def __init__(self, scene, inputs = None, outputs = None):
        super().__init__(scene, inputs, outputs)
        self.maya_node = None

    def getSubtitle(self):
        return "operator"

    def getOutputPlug(self):
        if self.maya_node is None or not MC.objectExists(self.maya_node):
            return None
        return "%s.%s" % (self.maya_node, self.__class__.output_attribute)

    def validate(self):
        #an operator with nothing feeding its first input produces a constant,
        #which is almost always a wiring mistake rather than an intent
        return self.setValidity(self.getUpstreamNode(0) is not None)

    def removeBuiltNodes(self):
        for maya_node in self.built_maya_nodes:
            if MC.objectExists(maya_node):
                MC.deleteNode(maya_node)
        self.maya_node = None
        self.built_maya_nodes = []

    def connectInputs(self):
        return True, ""

    def connectInputSocket(self, socket_index, target_node, target_attribute):
        """Wire whatever feeds this socket into target_node.target_attribute.
        Returns False when nothing is connected, so the caller can fall back to a
        constant instead."""
        upstream = self.getUpstreamNode(socket_index)
        if upstream is None:
            return False

        source_plug = upstream.getOutputPlug()
        if source_plug is None or target_node is None:
            return False

        source_node, source_attribute = source_plug.split(".", 1)
        MC.connectAttribute(source_node, source_attribute, target_node, target_attribute, force = True)
        return True


@registerAttributeNode(OPERATIONCODE_REVERSE_NODE)
class ReverseNode(OperatorNode):
    """1 - input. The usual way to make one visibility switch hide what another shows."""

    operation_code = OPERATIONCODE_REVERSE_NODE
    operation_title = "Reverse"
    output_attribute = "outputX"

    def getDescription(self):
        return "Outputs 1 - input.\nUse to invert a 0/1 value such as a visibility switch."

    def getNodeBaseName(self):
        return "attr_reverse_%s" % self.id

    def buildNode(self):
        self.removeBuiltNodes()
        self.maya_node = MC.createReverseNode(self.getNodeBaseName())
        self.built_maya_nodes = [self.maya_node]
        return True, ""

    def connectInputs(self):
        self.connectInputSocket(0, self.maya_node, "inputX")
        return True, ""


class MultiplyNodeProperties(AttributeNodeProperties):

    def initUI(self):
        super().initUI()
        self.layout.addWidget(QLabel("B value (used when B is unconnected):"))
        self.factor_spin_box = buildSpinBox(-1000.0, 1000.0, 1.0, self.onFactorChanged)
        self.layout.addWidget(self.factor_spin_box)

    def onFactorChanged(self, value):
        self.node.factor = value
        self.node.properties.refresh()
        self.setHasBeenModified()

    def refresh(self):
        super().refresh()
        if not hasattr(self, "factor_spin_box"):
            return
        self.factor_spin_box.blockSignals(True)
        self.factor_spin_box.setValue(self.node.factor)
        self.factor_spin_box.setEnabled(self.node.getUpstreamNode(1) is None)
        self.factor_spin_box.blockSignals(False)


@registerAttributeNode(OPERATIONCODE_MULTIPLY_NODE)
class MultiplyNode(OperatorNode):
    """A x B. Either input can be an attribute; B falls back to a constant when
    nothing is wired into it."""

    operation_code = OPERATIONCODE_MULTIPLY_NODE
    operation_title = "Multiply"
    output_attribute = "outputX"
    Node_Properties_Class = MultiplyNodeProperties

    def __init__(self, scene):
        super().__init__(scene,
                         inputs = [["A", SocketTypes.attribute, False],
                                   ["B", SocketTypes.attribute, False]],
                         outputs = [["out", SocketTypes.attribute, True]])
        self.factor = 1.0

    def getDescription(self):
        if self.getUpstreamNode(1) is not None:
            return "Outputs A x B."
        return "Outputs A x %s." % self.factor

    def getNodeBaseName(self):
        return "attr_multiply_%s" % self.id

    def buildNode(self):
        self.removeBuiltNodes()
        self.maya_node = MC.createMultiplyDivideNode(self.getNodeBaseName())
        MC.setAttribute(self.maya_node, "operation", 1)
        self.built_maya_nodes = [self.maya_node]
        return True, ""

    def connectInputs(self):
        self.connectInputSocket(0, self.maya_node, "input1X")

        #B only falls back to the constant when nothing is wired into it
        if not self.connectInputSocket(1, self.maya_node, "input2X"):
            MC.setAttribute(self.maya_node, "input2X", self.factor)
        return True, ""

    def serialize(self):
        result_data = super().serialize()
        result_data['factor'] = self.factor
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id = True, exists = False):
        result = super().deserialize(data, hashmap, restore_id, exists)
        self.factor = data.get('factor', 1.0)
        return result


class ConditionNodeProperties(AttributeNodeProperties):

    def initUI(self):
        super().initUI()

        self.layout.addWidget(QLabel("Operation:"))
        self.operation_combo = QComboBox()
        for label, key in ConditionNode.OPERATIONS:
            self.operation_combo.addItem(label, key)
        self.operation_combo.currentIndexChanged.connect(self.onOperationChanged)
        self.layout.addWidget(self.operation_combo)

        self.layout.addWidget(QLabel("B value (used when B is unconnected):"))
        self.second_value_spin_box = buildSpinBox(-1000.0, 1000.0, 0.5, self.onSecondValueChanged)
        self.layout.addWidget(self.second_value_spin_box)

        self.layout.addWidget(QLabel("Output when true:"))
        self.true_value_spin_box = buildSpinBox(-1000.0, 1000.0, 1.0, self.onTrueValueChanged)
        self.layout.addWidget(self.true_value_spin_box)

        self.layout.addWidget(QLabel("Output when false:"))
        self.false_value_spin_box = buildSpinBox(-1000.0, 1000.0, 0.0, self.onFalseValueChanged)
        self.layout.addWidget(self.false_value_spin_box)

    def onOperationChanged(self, index):
        self.node.operation = self.operation_combo.itemData(index)
        self.node.properties.refresh()
        self.setHasBeenModified()

    def onSecondValueChanged(self, value):
        self.node.second_value = value
        self.setHasBeenModified()

    def onTrueValueChanged(self, value):
        self.node.true_value = value
        self.setHasBeenModified()

    def onFalseValueChanged(self, value):
        self.node.false_value = value
        self.setHasBeenModified()

    def refresh(self):
        super().refresh()
        if not hasattr(self, "operation_combo"):
            return

        for widget in (self.operation_combo, self.second_value_spin_box,
                       self.true_value_spin_box, self.false_value_spin_box):
            widget.blockSignals(True)

        index = self.operation_combo.findData(self.node.operation)
        if index >= 0:
            self.operation_combo.setCurrentIndex(index)
        self.second_value_spin_box.setValue(self.node.second_value)
        self.second_value_spin_box.setEnabled(self.node.getUpstreamNode(1) is None)
        self.true_value_spin_box.setValue(self.node.true_value)
        self.false_value_spin_box.setValue(self.node.false_value)

        for widget in (self.operation_combo, self.second_value_spin_box,
                       self.true_value_spin_box, self.false_value_spin_box):
            widget.blockSignals(False)


@registerAttributeNode(OPERATIONCODE_CONDITION_NODE)
class ConditionNode(OperatorNode):
    """Compares A against B and outputs one of two values.

    The comparisons map straight onto Maya's `condition.operation`. The logical
    operators don't exist natively, so they are composed: AND multiplies the two
    terms and tests the product, OR sums them and tests the sum, and XOR is just
    'A is not equal to B', which is what exclusive-or means for 0/1 values.
    """

    operation_code = OPERATIONCODE_CONDITION_NODE
    operation_title = "Condition"
    output_attribute = "outColorR"
    Node_Properties_Class = ConditionNodeProperties

    #(label, key). The comparison keys are Maya's own condition.operation indices.
    OPERATIONS = [
        ("A == B", "equal"),
        ("A != B", "not_equal"),
        ("A >  B", "greater"),
        ("A >= B", "greater_or_equal"),
        ("A <  B", "less"),
        ("A <= B", "less_or_equal"),
        ("A and B", "and"),
        ("A or B", "or"),
        ("A xor B", "xor"),
    ]

    MAYA_OPERATION_INDEX = {
        "equal": 0, "not_equal": 1, "greater": 2,
        "greater_or_equal": 3, "less": 4, "less_or_equal": 5,
        #xor over 0/1 is exactly 'not equal'
        "xor": 1,
    }

    def __init__(self, scene):
        super().__init__(scene,
                         inputs = [["A", SocketTypes.attribute, False],
                                   ["B", SocketTypes.attribute, False]],
                         outputs = [["out", SocketTypes.attribute, True]])
        self.operation = "greater"
        self.second_value = 0.5
        self.true_value = 1.0
        self.false_value = 0.0

        #the combining node AND/OR need in front of the comparison
        self.combine_node = None

    def getOperationLabel(self):
        return next((label for label, key in self.OPERATIONS if key == self.operation), self.operation)

    def getDescription(self):
        #substituting the constant into the label itself produced "A or 0.5"
        label = self.getOperationLabel()
        if self.getUpstreamNode(1) is None:
            label += "  (B = %s)" % self.second_value
        return "Outputs %s when %s, otherwise %s." % (self.true_value, label, self.false_value)

    def getNodeBaseName(self):
        return "attr_condition_%s" % self.id

    def buildNode(self):
        self.removeBuiltNodes()

        #AND and OR have no native equivalent - combine the two terms first, then
        #test the combined value against zero with an ordinary condition
        if self.operation == "and":
            self.combine_node = MC.createMultiplyDivideNode(self.getNodeBaseName() + "_and")
            MC.setAttribute(self.combine_node, "operation", 1)
        elif self.operation == "or":
            self.combine_node = MC.createPlusMinusAverageNode(self.getNodeBaseName() + "_or")
            MC.setAttribute(self.combine_node, "operation", 1)
        else:
            self.combine_node = None

        self.maya_node = MC.createConditionNode(self.getNodeBaseName())

        if self.combine_node is not None:
            #combined value > 0 means "true" for both AND and OR
            MC.setAttribute(self.maya_node, "operation", 2)
            MC.setAttribute(self.maya_node, "secondTerm", 0.0)
        else:
            MC.setAttribute(self.maya_node, "operation", self.MAYA_OPERATION_INDEX[self.operation])

        MC.setAttribute(self.maya_node, "colorIfTrueR", self.true_value)
        MC.setAttribute(self.maya_node, "colorIfFalseR", self.false_value)

        self.built_maya_nodes = [node for node in (self.combine_node, self.maya_node) if node is not None]
        return True, ""

    def connectInputs(self):
        if self.combine_node is not None:
            if self.operation == "and":
                self.connectInputSocket(0, self.combine_node, "input1X")
                if not self.connectInputSocket(1, self.combine_node, "input2X"):
                    MC.setAttribute(self.combine_node, "input2X", self.second_value)
                MC.connectAttribute(self.combine_node, "outputX", self.maya_node, "firstTerm", force = True)
            else:
                self.connectInputSocket(0, self.combine_node, "input1D[0]")
                if not self.connectInputSocket(1, self.combine_node, "input1D[1]"):
                    MC.setAttribute(self.combine_node, "input1D[1]", self.second_value)
                MC.connectAttribute(self.combine_node, "output1D", self.maya_node, "firstTerm", force = True)
            return True, ""

        self.connectInputSocket(0, self.maya_node, "firstTerm")
        if not self.connectInputSocket(1, self.maya_node, "secondTerm"):
            MC.setAttribute(self.maya_node, "secondTerm", self.second_value)
        return True, ""

    def serialize(self):
        result_data = super().serialize()
        result_data['operation'] = self.operation
        result_data['second_value'] = self.second_value
        result_data['true_value'] = self.true_value
        result_data['false_value'] = self.false_value
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id = True, exists = False):
        result = super().deserialize(data, hashmap, restore_id, exists)
        stored_operation = data.get('operation', "greater")
        #older graphs stored Maya's numeric operation index
        if isinstance(stored_operation, int):
            stored_operation = next((key for key, index in self.MAYA_OPERATION_INDEX.items()
                                     if index == stored_operation), "greater")
        self.operation = stored_operation
        self.second_value = data.get('second_value', data.get('threshold', 0.5))
        self.true_value = data.get('true_value', 1.0)
        self.false_value = data.get('false_value', 0.0)
        return result


class ClampNodeProperties(AttributeNodeProperties):

    def initUI(self):
        super().initUI()
        self.layout.addWidget(QLabel("Minimum:"))
        self.minimum_spin_box = buildSpinBox(-1000.0, 1000.0, 0.0, self.onMinimumChanged)
        self.layout.addWidget(self.minimum_spin_box)

        self.layout.addWidget(QLabel("Maximum:"))
        self.maximum_spin_box = buildSpinBox(-1000.0, 1000.0, 1.0, self.onMaximumChanged)
        self.layout.addWidget(self.maximum_spin_box)

    def onMinimumChanged(self, value):
        self.node.minimum = value
        self.node.properties.refresh()
        self.setHasBeenModified()

    def onMaximumChanged(self, value):
        self.node.maximum = value
        self.node.properties.refresh()
        self.setHasBeenModified()

    def refresh(self):
        super().refresh()
        if not hasattr(self, "minimum_spin_box"):
            return
        for spin_box, value in ((self.minimum_spin_box, self.node.minimum),
                                (self.maximum_spin_box, self.node.maximum)):
            spin_box.blockSignals(True)
            spin_box.setValue(value)
            spin_box.blockSignals(False)


@registerAttributeNode(OPERATIONCODE_CLAMP_NODE)
class ClampNode(OperatorNode):
    """Holds the input between a minimum and a maximum."""

    operation_code = OPERATIONCODE_CLAMP_NODE
    operation_title = "Clamp"
    output_attribute = "outputR"
    Node_Properties_Class = ClampNodeProperties

    def __init__(self, scene):
        super().__init__(scene,
                         inputs = [["in", SocketTypes.attribute, False]],
                         outputs = [["out", SocketTypes.attribute, True]])
        self.minimum = 0.0
        self.maximum = 1.0

    def getDescription(self):
        return "Holds input between %s and %s." % (self.minimum, self.maximum)

    def getNodeBaseName(self):
        return "attr_clamp_%s" % self.id

    def buildNode(self):
        self.removeBuiltNodes()
        self.maya_node = MC.createClampNode(self.getNodeBaseName())
        MC.setAttribute(self.maya_node, "minR", self.minimum)
        MC.setAttribute(self.maya_node, "maxR", self.maximum)
        self.built_maya_nodes = [self.maya_node]
        return True, ""

    def connectInputs(self):
        self.connectInputSocket(0, self.maya_node, "inputR")
        return True, ""

    def serialize(self):
        result_data = super().serialize()
        result_data['minimum'] = self.minimum
        result_data['maximum'] = self.maximum
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id = True, exists = False):
        result = super().deserialize(data, hashmap, restore_id, exists)
        self.minimum = data.get('minimum', 0.0)
        self.maximum = data.get('maximum', 1.0)
        return result
