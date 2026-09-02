from PySide6.QtWidgets import QWidget, QSizePolicy, QHBoxLayout, QPushButton # type: ignore
from PySide6.QtCore import QSize, Qt # type: ignore

class SkinningEditorToolbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tab = parent

        self.initUI()

    def initUI(self):
        self.setMaximumHeight(50)

        self.layout = QHBoxLayout(self)

        self.add_skincluster_button = QPushButton("New SkinCluster")
        self.add_skincluster_button.clicked.connect(self.onAddSkinCluster)

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.onSelectAll)

        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.clicked.connect(self.onDeselectAll)

        self.remove_selected_button = QPushButton("Remove Selected")
        self.remove_selected_button.clicked.connect(self.onRemoveSelected)

        self.remove_all_button = QPushButton("Remove All")
        self.remove_all_button.clicked.connect(self.onRemoveAll)

        self.build_selected_button = QPushButton("Build Selected")
        self.build_selected_button.clicked.connect(self.onBuildSelected)

        self.build_all_button = QPushButton("Build All")
        self.build_all_button.clicked.connect(self.onBuildAll)

        self.accept_new_deformers = QPushButton("Accept New")
        self.accept_new_deformers.setStyleSheet("QPushButton { background-color: #FF2E6B2E; } QPushButton:disabled { background-color: #FF4D4D4D; color: #FF888888; }")
        self.accept_new_deformers.setEnabled(False)
        self.accept_new_deformers.clicked.connect(self.onAcceptNew)

        self.remove_deprecated_deformers = QPushButton("Remove Deprecated")
        self.remove_deprecated_deformers.setStyleSheet("QPushButton { background-color: #FF6B2E2E; } QPushButton:disabled { background-color: #FF4D4D4D; color: #FF888888; }")
        self.remove_deprecated_deformers.setEnabled(False)
        self.remove_deprecated_deformers.clicked.connect(self.onRemoveDeprecated)

        for button in (self.add_skincluster_button, self.select_all_button, self.deselect_all_button,
                       self.remove_selected_button, self.remove_all_button, self.build_selected_button,
                       self.build_all_button, self.accept_new_deformers, self.remove_deprecated_deformers):
            #without this, the buttons stretch to fill the toolbar's full width
            #instead of sizing to their text
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.layout.addWidget(button, alignment=Qt.AlignLeft)

        self.layout.addStretch()

    def onAddSkinCluster(self):
        default_name = "SkinCluster_%d" % (len(self.tab.skin_clusters) + 1)
        self.tab.addSkinCluster(default_name)
        self.tab.skincluster_object_list.rebuild()

    def onSelectAll(self):
        self.tab.selectAllSkinClusters()
        self.tab.skincluster_object_list.refreshAll()

    def onDeselectAll(self):
        self.tab.deselectAllSkinClusters()
        self.tab.skincluster_object_list.refreshAll()

    def onRemoveSelected(self):
        self.tab.removeSelectedSkinClusters()
        self.tab.skincluster_object_list.rebuild()

    def onRemoveAll(self):
        self.tab.removeAllSkinClusters()
        self.tab.skincluster_object_list.rebuild()

    def onBuildSelected(self):
        results = self.tab.buildSelectedSkinClusters()
        self.printBuildResults(results)

    def onBuildAll(self):
        results = self.tab.buildAllSkinClusters()
        self.printBuildResults(results)

    def printBuildResults(self, results):
        for skin_cluster, (success, message) in results.items():
            print("SkinningEditorToolbar:: build:: ", skin_cluster.cluster_name, "->", success, message)

    def onRemoveDeprecated(self):
        scene = self.tab.getScene()

        for skin_cluster in self.tab.skin_clusters:
            skin_cluster.removeStaleRefs(scene)

        self.tab.deformer_list.clearDeprecatedEntries()

        self.tab.setModified(True)
        self.tab.skincluster_object_list.rebuild()
        self.tab.updateRemoveDeprecatedButtonState()

    def onAcceptNew(self):
        #purely a display concern - doesn't touch any skin cluster's deform_refs,
        #just clears the "new" highlight now that it's been seen/acknowledged
        self.tab.deformer_list.acceptNewEntries()
        self.tab.setModified(True)
        self.tab.updateAcceptNewButtonState()
