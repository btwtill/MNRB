import os
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_StepNode import PipelineStepNode, PipelineStepProperties #type: ignore
from MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_conf import registerPipelineStep #type: ignore
from MNRB.ROSE_UI.node_Editor_UI.node_Editor_SocketTypes import SocketTypes #type: ignore
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore

OPERATIONCODE_OUTPUTPATHSTEP = 2


class OutputPathStepProperties(PipelineStepProperties):
    def __init__(self, node):
        super().__init__(node)
        self.output_directory = ""
        #optional - a transform whose whole subtree gets swept into the geometry
        #hierarchy for export alongside whatever the Skinning step already gathers,
        #then unparented back afterward. Lets the user include static/decorative
        #geometry that isn't bound to anything and so isn't a skinCluster target.
        self.geometry_root = None

    def initUI(self):
        super().initUI()

        output_label = QLabel("Output Directory:")
        self.layout.addWidget(output_label)

        output_row = QHBoxLayout()

        self.output_directory_edit = QLineEdit()
        self.output_directory_edit.setPlaceholderText("No output directory set")
        self.output_directory_edit.editingFinished.connect(self.onOutputDirectoryEdited)
        output_row.addWidget(self.output_directory_edit)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.onBrowseOutputDirectory)
        output_row.addWidget(self.browse_button)

        self.layout.addLayout(output_row)

        geometry_root_label = QLabel("Geometry Root:")
        self.layout.addWidget(geometry_root_label)

        geometry_root_row = QHBoxLayout()

        self.set_geometry_root_button = QPushButton("Set Geometry Root")
        self.set_geometry_root_button.clicked.connect(self.onSetGeometryRoot)
        geometry_root_row.addWidget(self.set_geometry_root_button)

        self.geometry_root_label = QLabel("No Geometry Root Selected")
        geometry_root_row.addWidget(self.geometry_root_label)
        geometry_root_row.addStretch()

        self.layout.addLayout(geometry_root_row)

    def onOutputDirectoryEdited(self):
        self.setOutputDirectory(self.output_directory_edit.text())

    def onBrowseOutputDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_directory_edit.setText(directory)
            self.setOutputDirectory(directory)

    def setOutputDirectory(self, directory):
        self.output_directory = directory
        self.setHasBeenModified()

    def onSetGeometryRoot(self):
        selection = MC.getViewportSelection()
        if len(selection) != 1:
            print("OutputPathStepProperties:: --onSetGeometryRoot:: Select exactly one node to use as the geometry root")
            return

        self.geometry_root = selection[0]
        self.geometry_root_label.setText(self.geometry_root)
        self.setHasBeenModified()

    def serialize(self):
        result_data = super().serialize()
        result_data['output_directory'] = self.output_directory
        result_data['geometry_root'] = self.geometry_root
        return result_data

    def deserialize(self, data, hashmap = {}, restore_id=True):
        result = super().deserialize(data, hashmap, restore_id)
        self.output_directory = data.get('output_directory', "")
        self.output_directory_edit.setText(self.output_directory)
        self.geometry_root = data.get('geometry_root', None)
        self.geometry_root_label.setText(self.geometry_root if self.geometry_root else "No Geometry Root Selected")
        return True


@registerPipelineStep(OPERATIONCODE_OUTPUTPATHSTEP)
class OutputPathStep(PipelineStepNode):
    """The pipeline's terminal node - holds the output directory for the full rig
    build and, on run, exports the scene there. Input only (nothing runs after
    packaging). At least one Output Path node must always remain in the graph,
    since a pipeline without a destination doesn't mean anything - see
    is_deletable below for the rule once more than one exists."""

    operation_code = OPERATIONCODE_OUTPUTPATHSTEP
    operation_title = "Output Path"
    icon = ""
    Node_Properties_Class = OutputPathStepProperties

    def __init__(self, scene):
        super().__init__(scene, inputs = [["In", SocketTypes.sequence, True]], outputs = [])
        #(node, original_parent_or_None), or None - consumed and cleared by
        #revertStep(), same pattern as SkinningStep's _reparent_actions
        self._geometry_root_revert_action = None

    @property
    def is_deletable(self):
        #deletable as soon as a sibling Output Path node exists to take over -
        #only the last remaining one is protected. Compares operation_code (a
        #plain int) rather than isinstance(node, OutputPathStep) - isinstance
        #breaks across importlib.reload(), same bug class fixed in SkinningStep's
        #hasEnabledOutputPathStep()
        output_path_nodes = [node for node in self.scene.nodes if node.operation_code == OPERATIONCODE_OUTPUTPATHSTEP]
        return len(output_path_nodes) > 1

    @is_deletable.setter
    def is_deletable(self, value):
        #NodeEditorNode.__init__ unconditionally assigns self.is_deletable - swallow
        #it here, deletability is always computed live from sibling count above
        pass

    def runStep(self):
        output_directory = self.properties.output_directory
        if not output_directory:
            return False, "No output directory set"

        if not os.path.isdir(output_directory):
            try:
                os.makedirs(output_directory)
            except Exception as e:
                return False, "Could not create output directory: %s" % e

        node_editor_tab = self.scene.node_editor_tab
        if node_editor_tab is None:
            return False, "No node editor tab available"

        rig_scene = node_editor_tab.central_widget.scene

        #export only the main rig hierarchy (skeleton/components/geometry all
        #live under it) so guides and other workfile helper nodes - which sit
        #outside it - never end up in the shipped file
        if not rig_scene.virtual_rig_hierarchy.rig_hierarchy_object.ensureExistence():
            return False, "Could not find/create the rig hierarchy - build the control rig first"

        self.moveGeometryRootUnderGeometryHierarchy(rig_scene)

        rig_hierarchy_name = rig_scene.virtual_rig_hierarchy.rig_hierarchy_object.name

        rig_name = "rig"
        configured_name = rig_scene.properties.getRigName()
        if configured_name and configured_name != "Undefined":
            rig_name = configured_name

        file_path = os.path.join(output_directory, "%s.mb" % rig_name)

        try:
            MC.clearSelection()
            MC.selectObject(rig_hierarchy_name)
            MC.exportSelectedAs(file_path)
            MC.clearSelection()
        except Exception as e:
            return False, "Export failed: %s" % e

        return True, "Exported to %s" % file_path

    def moveGeometryRootUnderGeometryHierarchy(self, rig_scene):
        geometry_root = self.properties.geometry_root
        if not geometry_root or not MC.objectExists(geometry_root):
            return

        virtual_rig_hierarchy = rig_scene.virtual_rig_hierarchy
        virtual_rig_hierarchy.geometry_hierarchy_object.ensureExistence()
        geometry_group = virtual_rig_hierarchy.geometry_hierarchy_object.name

        current_parent = MC.getObjectParentNode(geometry_root)
        original_parent = current_parent[0] if current_parent else None
        if original_parent == geometry_group:
            return

        MC.parentObject(geometry_root, geometry_group)
        self._geometry_root_revert_action = (geometry_root, original_parent)

    def revertStep(self):
        if self._geometry_root_revert_action is None:
            return

        node, original_parent = self._geometry_root_revert_action
        self._geometry_root_revert_action = None

        if not MC.objectExists(node):
            return

        if original_parent is not None and MC.objectExists(original_parent):
            MC.parentObject(node, original_parent)
        else:
            MC.unparentObject(node)

    def deserialize(self, data, hashmap = {}, restore_id = True, exists = False):
        return super().deserialize(data, hashmap, restore_id, exists)
