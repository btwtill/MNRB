from PySide6.QtCore import Qt #type: ignore
from MNRB.ROSE_Nodes.rose_node_base import ROSE_NodeProperties #type: ignore
from MNRB.ROSE_naming.ROSE_names import ROSE_Names #type: ignore

CLASS_DEBUG = False

MIXED_PLACEHOLDER = "- mixed -"

class MultiEdit_PropertyWidget(ROSE_NodeProperties):
    """The properties panel shown while several component nodes are selected.

    Subclasses ROSE_NodeProperties purely to reuse its layout - every field is
    re-pointed at the whole selection instead of one node. Two rules hold
    throughout: a field whose nodes disagree shows a mixed state rather than
    silently displaying the first node's value, and every write goes through the
    target node's own apply* method rather than poking its widgets directly, so
    the single-edit and multi-edit paths can't drift apart.
    """

    def __init__(self, graphic_nodes = [], parent = None):
        #ROSE_NodeProperties needs a node during __init__ (initUI/initActions run
        #from it), and self.nodes can't be assigned before that - PySide6 refuses
        #attribute writes on a QWidget whose base __init__ hasn't run. Everything
        #that reads self.nodes is either an event handler (fires later) or called
        #below, and hasSelection() guards the rest.
        super().__init__(graphic_nodes[0].node)

        self.nodes = [graphic_node.node for graphic_node in graphic_nodes]

        #unlike the other three checkboxes, "Disable Component" has no handler on
        #its own signal - the base class reaches it through the has_been_modified
        #callback, which fires for every edit. Pushing the selection's disabled
        #state from there would re-apply it on unrelated changes (a size drag,
        #say), so this needs its own connection.
        self.disabled_checkbox.stateChanged.connect(self.onDisabledCheckboxChanged)

        self.setTitleForSelection()
        self.disableSingleNodeOnlyFields()
        self.showSharedState()
        self.validateProperties()

        if CLASS_DEBUG:
            print("%s:: __init__:: editing %d nodes" % (self.__class__.__name__, len(self.nodes)))
            for node in self.nodes:
                print("%s:: \t" % self.__class__.__name__, node)

    def hasSelection(self):
        #inherited callbacks are connected during __init__ and can fire before
        #self.nodes exists
        return getattr(self, "nodes", None) is not None

    def setTitleForSelection(self):
        title = "Multi Edit: %d Components" % len(self.nodes)

        operation_titles = set(node.__class__.operation_title for node in self.nodes)
        if len(operation_titles) > 1:
            #only ROSE_NodeProperties' own fields are shown, so anything a
            #subclass adds (e.g. the multi deform chain-length slider) isn't here
            title += " (mixed types - shared settings only)"

        self.title = title

    def disableSingleNodeOnlyFields(self):
        #component names have to stay unique - validateDuplicates() invalidates
        #every node that shares one - so there is no sane multi-edit meaning for
        #this field. The side prefix next to it stays editable.
        self.component_name_edit.blockSignals(True)
        self.component_name_edit.clear()
        self.component_name_edit.setEnabled(False)
        self.component_name_edit.setPlaceholderText("Names stay per-component")
        self.component_name_edit.blockSignals(False)

# Reading the selection's shared state

    def getSharedValue(self, read_property):
        """The value all selected nodes agree on, or None if they disagree."""
        values = [read_property(node.properties) for node in self.nodes]
        first_value = values[0]
        return first_value if all(value == first_value for value in values) else None

    def showSharedState(self):
        self.showSharedSize(self.guide_slider_size_edit, self.guide_size_slider,
                            self.getSharedValue(lambda properties: properties.guide_size))
        self.showSharedSize(self.deform_slider_size_edit, self.deform_size_slider,
                            self.getSharedValue(lambda properties: properties.deform_size))
        self.showSharedSize(self.control_slider_size_edit, self.control_size_slider,
                            self.getSharedValue(lambda properties: properties.control_size))

        self.showSharedCheckbox(self.disabled_checkbox,
                                self.getSharedValue(lambda properties: properties.is_disabled))
        self.showSharedCheckbox(self.display_guide_orientation_checkbox,
                                self.getSharedValue(lambda properties: properties.displayGuideOrientation))
        self.showSharedCheckbox(self.auto_orient_guide_checkbox,
                                self.getSharedValue(lambda properties: properties.autoOrientGuide))
        self.showSharedCheckbox(self.extended_rotation_control_checkbox,
                                self.getSharedValue(lambda properties: properties.display_extended_rotation_controls))

        self.showSharedColor(self.getSharedValue(lambda properties: properties.component_color.name))
        self.showSharedSidePrefix(self.getSharedValue(lambda properties: properties.component_side_prefix))

    def showSharedSize(self, size_edit, size_slider, value):
        #signals blocked throughout: these are programmatic writes describing the
        #current state, not user edits, and must not push anything back onto the nodes
        size_edit.blockSignals(True)
        size_slider.blockSignals(True)

        if value is None:
            size_edit.clear()
            size_edit.setPlaceholderText(MIXED_PLACEHOLDER)
        else:
            size_edit.setText(str(value))
            size_slider.setValue(self.formatSliderEditToSliderValue(str(value)))

        size_slider.blockSignals(False)
        size_edit.blockSignals(False)

    def showSharedCheckbox(self, checkbox, value):
        checkbox.blockSignals(True)

        if value is None:
            checkbox.setTristate(True)
            checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
        else:
            checkbox.setTristate(False)
            checkbox.setChecked(value)

        checkbox.blockSignals(False)

    def showSharedColor(self, color_name):
        self.component_color_dropdown.blockSignals(True)
        #index -1 leaves the combo blank, which is how "no single shared color" reads
        if color_name is None:
            self.component_color_dropdown.setCurrentIndex(-1)
        else:
            self.component_color_dropdown.setCurrentText(color_name)
        self.component_color_dropdown.blockSignals(False)

    def showSharedSidePrefix(self, prefix):
        buttons_by_prefix = {
            ROSE_Names.left.prefix: self.left_prefix_button,
            ROSE_Names.middle.prefix: self.mid_prefix_button,
            ROSE_Names.right.prefix: self.right_prefix_button,
        }

        for button in buttons_by_prefix.values():
            button.markDeselected()

        #mixed sides leave all three unmarked, so nothing claims to be the side
        if prefix in buttons_by_prefix:
            buttons_by_prefix[prefix].mark()

    def readCheckboxValue(self, checkbox):
        #a click on a mixed (partially checked) box resolves it to a definite
        #state for the whole selection, so tristate is switched back off here
        value = checkbox.checkState() == Qt.CheckState.Checked
        checkbox.setTristate(False)
        return value

# Writing back to every selected node

    def validateProperties(self):
        #this panel has no component name of its own to validate - it's valid
        #exactly when every node it edits is
        if not self.hasSelection(): return False

        is_valid = all(node.properties.is_valid for node in self.nodes)
        self.is_valid = is_valid
        return is_valid

    def updateComponentName(self):
        #the name field is disabled, so the only thing that reaches here is one of
        #the side prefix buttons, which set self.component_side_prefix via mark()
        if not self.hasSelection(): return

        for node in self.nodes:
            node.properties.applySidePrefix(self.component_side_prefix)

        #a prefix change can make two components share a name - revalidate after
        #the nodes have actually been updated, not from the modified callback that
        #ran before this
        self.validateProperties()

    def updateComponentColor(self, index):
        if not self.hasSelection(): return
        if index < 0: return

        for node in self.nodes:
            node.properties.applyComponentColor(index)

    def onDisabledCheckboxChanged(self):
        if not self.hasSelection(): return

        value = self.readCheckboxValue(self.disabled_checkbox)
        self.is_disabled = value
        for node in self.nodes:
            node.properties.applyDisabled(value)

        #a disabled component is an invalid one, so the build buttons follow
        self.validateProperties()

    def setGuideOrientationShapeDisplay(self):
        if not self.hasSelection(): return

        value = self.readCheckboxValue(self.display_guide_orientation_checkbox)
        self.displayGuideOrientation = value
        for node in self.nodes:
            node.properties.applyDisplayGuideOrientation(value)

    def setAutoGuideOrientation(self):
        if not self.hasSelection(): return

        value = self.readCheckboxValue(self.auto_orient_guide_checkbox)
        self.autoOrientGuide = value
        for node in self.nodes:
            node.properties.applyAutoOrientGuide(value)

    def setExtendedRotationControlDisplay(self):
        if not self.hasSelection(): return

        #the previous implementation inverted each node's own checkbox instead of
        #setting them all to one state, so a mixed selection just stayed mixed
        value = self.readCheckboxValue(self.extended_rotation_control_checkbox)
        self.display_extended_rotation_controls = value
        for node in self.nodes:
            node.properties.applyExtendedRotationControlDisplay(value)

    def updateGuideSize(self):
        if not self.hasSelection(): return

        value = self.parseSizeEditValue(self.guide_slider_size_edit)
        if value is None: return

        self.guide_size = value
        for node in self.nodes:
            node.properties.applyGuideSize(value)

    def updateDeformSize(self):
        if not self.hasSelection(): return

        value = self.parseSizeEditValue(self.deform_slider_size_edit)
        if value is None: return

        self.deform_size = value
        for node in self.nodes:
            node.properties.applyDeformSize(value)

    def updateControlSize(self):
        if not self.hasSelection(): return

        value = self.parseSizeEditValue(self.control_slider_size_edit)
        if value is None: return

        self.control_size = value
        for node in self.nodes:
            node.properties.applyControlSize(value)

# Build actions

    def onBuildGuides(self):
        if not self.hasSelection(): return
        for node in self.nodes:
            #each node's own disabled state decides, not this panel's
            if not node.properties.is_disabled:
                node.guideBuild()

    def onBuildStatic(self):
        if not self.hasSelection(): return
        for node in self.nodes:
            if not node.properties.is_disabled:
                node.staticBuild()

    def onBuildComponent(self):
        if not self.hasSelection(): return
        for node in self.nodes:
            if not node.properties.is_disabled:
                node.componentBuild()

    def onConnectComponents(self):
        if not self.hasSelection(): return
        for node in self.nodes:
            if not node.properties.is_disabled:
                node.connectComponent()
