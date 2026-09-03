from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QCheckBox, QComboBox, QSpinBox, QSizePolicy, QMessageBox #type: ignore
from PySide6.QtCore import Qt #type: ignore

#Maya's own skinCluster bind-option choices - see MC.createSkinCluster for the
#flags these map to
BIND_METHOD_CHOICES = [("Closest Distance", 0), ("Closest in Hierarchy", 1), ("Heat Map", 2), ("Geodesic Voxel", 3)]
SKIN_METHOD_CHOICES = [("Classic Linear", 0), ("Dual Quaternion", 1), ("Weight Blended", 2)]
NORMALIZE_WEIGHTS_CHOICES = [("None", 0), ("Interactive", 1), ("Post", 2)]
WEIGHT_DISTRIBUTION_CHOICES = [("Distance", 0), ("Neighbors", 1)]
CONSTRAINT_TYPE_CHOICES = [("Native (Parent Constraint)", "native"), ("Matrix (live offset link)", "matrix")]

#deselected/selected use a background distinct from the surrounding list/app
#background (both are dark near-blacks) so a box reads as its own "card". The
#selected border reuses #FFFFA637 - the same amber ROSE already uses for
#selected nodes/edges in the node graph - rather than introducing a new color,
#and specifically not the app's own green (#FF336600), which already means
#"valid" elsewhere and would be misleading here.
BOX_BACKGROUND = "#FF3D3D3D"
DESELECTED_BORDER = "#FF666666"
SELECTED_BORDER = "#FFFFA637"

SELECTED_STYLE = "QWidget#skinClusterBox { border: 3px solid %s; border-radius: 4px; background-color: %s; }" % (SELECTED_BORDER, BOX_BACKGROUND)
DESELECTED_STYLE = "QWidget#skinClusterBox { border: 1px solid %s; border-radius: 4px; background-color: %s; }" % (DESELECTED_BORDER, BOX_BACKGROUND)

class SkinClusterComponentWidget(QWidget):
    """One skinCluster container 'box' in the skinning tab's cluster list.
    Displays/edits a single SkinningEditorCluster - clicking anywhere on the box
    (outside its interactive child widgets) toggles selection."""

    def __init__(self, skin_cluster, tab, parent=None):
        super().__init__(parent)

        self.skin_cluster = skin_cluster
        self.tab = tab

        #styling is scoped to this object name so the border/background rule
        #doesn't cascade down into the child labels/buttons/line edit
        self.setObjectName("skinClusterBox")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.initUI()
        self.refresh()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)

        self.setMinimumHeight(90)

        header_layout = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setMinimumHeight(24)
        self.name_edit.editingFinished.connect(self.onNameEdited)
        header_layout.addWidget(self.name_edit)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Skin Cluster", "skin")
        self.mode_combo.addItem("Constraint", "constraint")
        self.mode_combo.currentIndexChanged.connect(self.onModeChanged)
        header_layout.addWidget(self.mode_combo)

        self.layout.addLayout(header_layout)

        target_layout = QHBoxLayout()
        self.set_target_button = QPushButton("Set Target")
        self.set_target_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.set_target_button.clicked.connect(self.onSetTarget)
        target_layout.addWidget(self.set_target_button)

        self.target_label = QLabel("No Target Selected")
        target_layout.addWidget(self.target_label)
        target_layout.addStretch()

        self.layout.addLayout(target_layout)

        self.initSkinOptionsUI()
        self.initConstraintOptionsUI()

        self.deform_list_layout = QVBoxLayout()
        self.deform_list_layout.setSpacing(2)
        self.layout.addLayout(self.deform_list_layout)

    def initSkinOptionsUI(self):
        self.skin_options_widget = QWidget()
        skin_options_layout = QVBoxLayout(self.skin_options_widget)
        skin_options_layout.setContentsMargins(0, 0, 0, 0)
        skin_options_layout.setSpacing(4)

        auto_apply_row = QHBoxLayout()
        self.auto_apply_checkbox = QCheckBox("Auto-apply weights")
        self.auto_apply_checkbox.stateChanged.connect(self.onAutoApplyChanged)
        auto_apply_row.addWidget(self.auto_apply_checkbox)
        auto_apply_row.addStretch()
        skin_options_layout.addLayout(auto_apply_row)

        bind_row = QHBoxLayout()
        self.bind_method_combo = self.buildOptionCombo(BIND_METHOD_CHOICES, self.onBindMethodChanged)
        bind_row.addWidget(QLabel("Bind Method:"))
        bind_row.addWidget(self.bind_method_combo)
        self.skin_method_combo = self.buildOptionCombo(SKIN_METHOD_CHOICES, self.onSkinMethodChanged)
        bind_row.addWidget(QLabel("Skinning Method:"))
        bind_row.addWidget(self.skin_method_combo)
        bind_row.addStretch()
        skin_options_layout.addLayout(bind_row)

        weight_row = QHBoxLayout()
        self.normalize_weights_combo = self.buildOptionCombo(NORMALIZE_WEIGHTS_CHOICES, self.onNormalizeWeightsChanged)
        weight_row.addWidget(QLabel("Normalize Weights:"))
        weight_row.addWidget(self.normalize_weights_combo)
        self.weight_distribution_combo = self.buildOptionCombo(WEIGHT_DISTRIBUTION_CHOICES, self.onWeightDistributionChanged)
        weight_row.addWidget(QLabel("Weight Distribution:"))
        weight_row.addWidget(self.weight_distribution_combo)
        weight_row.addStretch()
        skin_options_layout.addLayout(weight_row)

        influence_row = QHBoxLayout()
        influence_row.addWidget(QLabel("Max Influences:"))
        self.max_influences_spinbox = QSpinBox()
        self.max_influences_spinbox.setRange(1, 64)
        self.max_influences_spinbox.valueChanged.connect(self.onMaxInfluencesChanged)
        influence_row.addWidget(self.max_influences_spinbox)

        self.maintain_max_influences_checkbox = QCheckBox("Maintain Max Influences")
        self.maintain_max_influences_checkbox.stateChanged.connect(self.onMaintainMaxInfluencesChanged)
        influence_row.addWidget(self.maintain_max_influences_checkbox)

        self.allow_multiple_bind_poses_checkbox = QCheckBox("Allow Multiple Bind Poses")
        self.allow_multiple_bind_poses_checkbox.stateChanged.connect(self.onAllowMultipleBindPosesChanged)
        influence_row.addWidget(self.allow_multiple_bind_poses_checkbox)
        influence_row.addStretch()
        skin_options_layout.addLayout(influence_row)

        weights_layout = QHBoxLayout()
        self.store_weights_button = QPushButton("Store Weights")
        self.store_weights_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.store_weights_button.clicked.connect(self.onStoreWeights)
        weights_layout.addWidget(self.store_weights_button)

        self.apply_weights_button = QPushButton("Apply Weights")
        self.apply_weights_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.apply_weights_button.clicked.connect(self.onApplyWeights)
        weights_layout.addWidget(self.apply_weights_button)

        self.remove_weights_button = QPushButton("Remove Stored Weights")
        self.remove_weights_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.remove_weights_button.clicked.connect(self.onRemoveStoredWeights)
        weights_layout.addWidget(self.remove_weights_button)

        self.weights_status_label = QLabel("Weights: Not stored yet")
        weights_layout.addWidget(self.weights_status_label)
        weights_layout.addStretch()
        skin_options_layout.addLayout(weights_layout)

        self.layout.addWidget(self.skin_options_widget)

    def initConstraintOptionsUI(self):
        self.constraint_options_widget = QWidget()
        constraint_options_layout = QHBoxLayout(self.constraint_options_widget)
        constraint_options_layout.setContentsMargins(0, 0, 0, 0)

        constraint_options_layout.addWidget(QLabel("Constraint Type:"))
        self.constraint_type_combo = self.buildOptionCombo(CONSTRAINT_TYPE_CHOICES, self.onConstraintTypeChanged)
        constraint_options_layout.addWidget(self.constraint_type_combo)
        constraint_options_layout.addStretch()

        self.layout.addWidget(self.constraint_options_widget)

    def buildOptionCombo(self, choices, on_changed_callback):
        combo = QComboBox()
        for label, value in choices:
            combo.addItem(label, value)
        combo.currentIndexChanged.connect(on_changed_callback)
        return combo

    def onNameEdited(self):
        self.skin_cluster.cluster_name = self.name_edit.text()
        self.tab.setModified(True)

    def onAutoApplyChanged(self):
        self.skin_cluster.auto_apply_weights = self.auto_apply_checkbox.isChecked()
        self.tab.setModified(True)

    def onModeChanged(self):
        self.skin_cluster.connection_type = self.mode_combo.currentData()
        self.tab.setModified(True)
        #shown/hidden option groups change this box's height - go through the
        #outer list's full rebuild, same as onRemoveDeform does for the same reason
        self.tab.skincluster_object_list.rebuild()

    def onConstraintTypeChanged(self):
        self.skin_cluster.constraint_type = self.constraint_type_combo.currentData()
        self.tab.setModified(True)

    def onBindMethodChanged(self):
        self.skin_cluster.bind_method = self.bind_method_combo.currentData()
        self.tab.setModified(True)

    def onSkinMethodChanged(self):
        self.skin_cluster.skin_method = self.skin_method_combo.currentData()
        self.tab.setModified(True)

    def onNormalizeWeightsChanged(self):
        self.skin_cluster.normalize_weights = self.normalize_weights_combo.currentData()
        self.tab.setModified(True)

    def onWeightDistributionChanged(self):
        self.skin_cluster.weight_distribution = self.weight_distribution_combo.currentData()
        self.tab.setModified(True)

    def onMaxInfluencesChanged(self):
        self.skin_cluster.maximum_influences = self.max_influences_spinbox.value()
        self.tab.setModified(True)

    def onMaintainMaxInfluencesChanged(self):
        self.skin_cluster.obey_maximum_influences = self.maintain_max_influences_checkbox.isChecked()
        self.tab.setModified(True)

    def onAllowMultipleBindPosesChanged(self):
        self.skin_cluster.allow_multiple_bind_poses = self.allow_multiple_bind_poses_checkbox.isChecked()
        self.tab.setModified(True)

    def onSetTarget(self):
        success, message = self.skin_cluster.setTargetFromSelection()
        if not success:
            print("SkinClusterComponentWidget:: --onSetTarget:: ", message)
        else:
            self.tab.setModified(True)
        self.refresh()

    def getWeightsFolder(self):
        if not self.tab.weights_folder_path:
            print("SkinClusterComponentWidget:: No project weights folder known yet - open or save the project first")
            return None
        return self.tab.weights_folder_path

    def onStoreWeights(self):
        weights_folder = self.getWeightsFolder()
        if weights_folder is None:
            return

        success, result = self.skin_cluster.exportWeights(weights_folder)
        if success:
            self.tab.setModified(True)
        print("SkinClusterComponentWidget:: --onStoreWeights:: ", success, result)
        self.refresh()

    def onApplyWeights(self):
        weights_folder = self.getWeightsFolder()
        if weights_folder is None:
            return

        success, result = self.skin_cluster.importWeights(weights_folder)
        print("SkinClusterComponentWidget:: --onApplyWeights:: ", success, result)

    def onRemoveStoredWeights(self):
        weights_folder = self.getWeightsFolder()
        if weights_folder is None:
            return

        confirmation = QMessageBox.question(
            self,
            "Remove Stored Weights",
            "Permanently delete the stored skin weights for '%s'?\nThis cannot be undone." % self.skin_cluster.cluster_name,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirmation != QMessageBox.Yes:
            return

        success, result = self.skin_cluster.removeStoredWeights(weights_folder)
        if success:
            self.tab.setModified(True)
        print("SkinClusterComponentWidget:: --onRemoveStoredWeights:: ", success, result)
        self.refresh()

    def onRemoveDeform(self, deform_id):
        self.skin_cluster.removeDeform(deform_id)
        self.tab.setModified(True)
        #the deform count changing means this box's overall size changes too - a
        #plain refresh() doesn't tell the owning QListWidgetItem to recompute its
        #size hint, so go through the outer list's full rebuild instead
        self.tab.skincluster_object_list.rebuild()

    def mousePressEvent(self, event):
        #child widgets (name edit, buttons) consume their own clicks before this
        #ever fires, so this only triggers for clicks on the box's empty background.
        #Plain click: exclusive select (this one only). Shift+click: additive toggle.
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.skin_cluster.is_selected = not self.skin_cluster.is_selected
            self.updateSelectionStyle()
        else:
            self.tab.deselectAllSkinClusters()
            self.skin_cluster.is_selected = True
            self.tab.skincluster_object_list.refreshAll()
        self.tab.notifySelectionChanged()
        super().mousePressEvent(event)

    def updateSelectionStyle(self):
        self.setStyleSheet(SELECTED_STYLE if self.skin_cluster.is_selected else DESELECTED_STYLE)

    def updateWeightsStatusLabel(self):
        weights_folder = self.tab.weights_folder_path
        if weights_folder and self.skin_cluster.hasStoredWeights(weights_folder):
            self.weights_status_label.setText("Weights: Stored")
        else:
            self.weights_status_label.setText("Weights: Not stored yet")

    def setComboToValue(self, combo, value):
        index = combo.findData(value)
        if index < 0:
            return
        #setting the index programmatically fires currentIndexChanged just like a
        #user edit would - block it here, otherwise onModeChanged's rebuild() call
        #re-enters rebuild() from inside its own loop (every widget it constructs
        #calls refresh() -> here) and deletes the QListWidgetItem out from under
        #the outer call that's still using it
        combo.blockSignals(True)
        combo.setCurrentIndex(index)
        combo.blockSignals(False)

    def setCheckedSilently(self, checkbox, checked):
        checkbox.blockSignals(True)
        checkbox.setChecked(checked)
        checkbox.blockSignals(False)

    def refresh(self):
        self.name_edit.setText(self.skin_cluster.cluster_name)
        self.target_label.setText(self.skin_cluster.target_mesh if self.skin_cluster.target_mesh else "No Target Selected")
        self.updateSelectionStyle()

        self.setComboToValue(self.mode_combo, self.skin_cluster.connection_type)
        is_skin_mode = self.skin_cluster.connection_type == "skin"
        self.skin_options_widget.setVisible(is_skin_mode)
        self.constraint_options_widget.setVisible(not is_skin_mode)

        if is_skin_mode:
            self.setCheckedSilently(self.auto_apply_checkbox, self.skin_cluster.auto_apply_weights)
            self.setComboToValue(self.bind_method_combo, self.skin_cluster.bind_method)
            self.setComboToValue(self.skin_method_combo, self.skin_cluster.skin_method)
            self.setComboToValue(self.normalize_weights_combo, self.skin_cluster.normalize_weights)
            self.setComboToValue(self.weight_distribution_combo, self.skin_cluster.weight_distribution)

            self.max_influences_spinbox.blockSignals(True)
            self.max_influences_spinbox.setValue(self.skin_cluster.maximum_influences)
            self.max_influences_spinbox.blockSignals(False)

            self.setCheckedSilently(self.maintain_max_influences_checkbox, self.skin_cluster.obey_maximum_influences)
            self.setCheckedSilently(self.allow_multiple_bind_poses_checkbox, self.skin_cluster.allow_multiple_bind_poses)
            self.updateWeightsStatusLabel()
        else:
            self.setComboToValue(self.constraint_type_combo, self.skin_cluster.constraint_type)

        while self.deform_list_layout.count():
            item = self.deform_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        #resolved against the live scene once per refresh, so rows referencing a
        #deform that's genuinely gone (not just renamed/rebuilt - resolveDeforms
        #already tolerates those) can be flagged
        _, unresolved_refs = self.skin_cluster.resolveDeforms(self.tab.getScene())
        stale_ids = set(ref["id"] for ref in unresolved_refs)

        for ref in self.skin_cluster.deform_refs:
            row = QHBoxLayout()

            label = QLabel(ref["name"])
            row.addWidget(label)
            row.addStretch()

            remove_button = QPushButton("x")
            remove_button.setFixedWidth(20)
            remove_button.clicked.connect(lambda checked=False, deform_id=ref["id"]: self.onRemoveDeform(deform_id))
            row.addWidget(remove_button)

            row_widget = QWidget()
            row_widget.setLayout(row)

            if ref["id"] in stale_ids:
                row_widget.setAttribute(Qt.WA_StyledBackground, True)
                row_widget.setStyleSheet("background-color: #FF6B2E2E;")

            self.deform_list_layout.addWidget(row_widget)
