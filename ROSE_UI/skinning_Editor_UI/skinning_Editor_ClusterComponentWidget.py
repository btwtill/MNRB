from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QCheckBox, QSizePolicy, QMessageBox #type: ignore
from PySide6.QtCore import Qt #type: ignore

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

        self.auto_apply_checkbox = QCheckBox("Auto-apply weights")
        header_layout.addWidget(self.auto_apply_checkbox)
        self.auto_apply_checkbox.stateChanged.connect(self.onAutoApplyChanged)

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

        self.layout.addLayout(weights_layout)

        self.deform_list_layout = QVBoxLayout()
        self.deform_list_layout.setSpacing(2)
        self.layout.addLayout(self.deform_list_layout)

    def onNameEdited(self):
        self.skin_cluster.cluster_name = self.name_edit.text()
        self.tab.setModified(True)

    def onAutoApplyChanged(self):
        self.skin_cluster.auto_apply_weights = self.auto_apply_checkbox.isChecked()
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

    def refresh(self):
        self.name_edit.setText(self.skin_cluster.cluster_name)
        self.auto_apply_checkbox.setChecked(self.skin_cluster.auto_apply_weights)
        self.target_label.setText(self.skin_cluster.target_mesh if self.skin_cluster.target_mesh else "No Target Selected")
        self.updateSelectionStyle()
        self.updateWeightsStatusLabel()

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
