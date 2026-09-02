from PySide6 import QtWidgets #type: ignore
from MNRB.MNRB_UI.node_Editor_UI.node_Editor_PropertiesWidget import NodeEditorPropertiesWidget #type: ignore

CLASS_DEBUG = False

class PipelineEditorSceneProperties(NodeEditorPropertiesWidget):
    """Mirrors NodeEditorSceneProperties' role (node_Editor_UI/node_Editor_SceneProperties.py)
    but for the pipeline canvas - no rig-name/validation/guide-static-component-connect
    buttons, since none of that applies. The output directory setting itself lives
    on the OutputPathStep node, not here - this just owns the "Build Full Pipeline"
    trigger and a run-status readout."""

    def __init__(self, scene, parent=None) -> None:
        super().__init__(parent)

        self.scene = scene
        self.title = "Pipeline Settings"

    def initUI(self):
        info_label = QtWidgets.QLabel("Add an Output Path step to set where the built rig gets exported.")
        info_label.setWordWrap(True)
        self.layout.addWidget(info_label)

    def initActions(self):
        self.build_pipeline_button = QtWidgets.QPushButton("Build Full Pipeline")
        self.build_pipeline_button.clicked.connect(self.onBuildFullPipeline)
        self.layout.addWidget(self.build_pipeline_button)

        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setWordWrap(True)
        self.layout.addWidget(self.status_label)

        self.setLayout(self.layout)

    def onBuildFullPipeline(self):
        results = self.scene.buildFullPipeline()

        lines = []
        for node, success, message in results:
            if success is None:
                lines.append("%s: skipped" % node.title)
            elif success:
                lines.append("%s: OK" % node.title)
            else:
                lines.append("%s: FAILED - %s" % (node.title, message))

        summary = " | ".join(lines) if lines else "No steps to run"
        self.status_label.setText(summary)
        if CLASS_DEBUG: print("PIPELINE_EDITOR_SCENE_PROPERTIES:: --onBuildFullPipeline:: ", summary)
