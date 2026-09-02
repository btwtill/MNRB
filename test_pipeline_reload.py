"""
Diagnostic: force-reload the full pipeline module chain (including the
package_output_step -> output_path_step rename), print what's actually
registered/loaded, then close any open MNRB editor window and reopen a fresh one.

Paste into Maya's Script Editor and run. Not part of the MNRB package.
"""

import sys
import importlib
from PySide6.QtWidgets import QApplication #type: ignore

# drop any stale cached entry for the deleted module outright, in case it's
# still sitting in sys.modules from before the rename
stale_module_name = "MNRB.MNRB_UI.pipeline_Editor_UI.steps.package_output_step"
if stale_module_name in sys.modules:
    print("Found stale cached module, removing:", stale_module_name)
    del sys.modules[stale_module_name]
else:
    print("No stale package_output_step module cached - good.")

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node as NodeEditorNode #type: ignore
importlib.reload(NodeEditorNode)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket as NodeEditorSocket #type: ignore
importlib.reload(NodeEditorSocket)

import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicView as NodeEditorQGraphicView #type: ignore
importlib.reload(NodeEditorQGraphicView)

import MNRB.MNRB_UI.pipeline_Editor_UI.pipeline_Editor_StepGraphicNode as PipelineEditorStepGraphicNode #type: ignore
importlib.reload(PipelineEditorStepGraphicNode)

import MNRB.MNRB_UI.pipeline_Editor_UI.pipeline_Editor_StepNode as PipelineEditorStepNode #type: ignore
importlib.reload(PipelineEditorStepNode)

import MNRB.MNRB_UI.pipeline_Editor_UI.pipeline_Editor_conf as PipelineEditorConf #type: ignore
importlib.reload(PipelineEditorConf)

import MNRB.MNRB_UI.pipeline_Editor_UI.steps.control_rig_step as ControlRigStep #type: ignore
importlib.reload(ControlRigStep)

import MNRB.MNRB_UI.pipeline_Editor_UI.steps.skinning_step as SkinningStep #type: ignore
importlib.reload(SkinningStep)

import MNRB.MNRB_UI.pipeline_Editor_UI.steps.output_path_step as OutputPathStep #type: ignore
importlib.reload(OutputPathStep)

import MNRB.MNRB_UI.pipeline_Editor_UI.pipeline_Editor_SceneProperties as PipelineEditorSceneProperties #type: ignore
importlib.reload(PipelineEditorSceneProperties)

import MNRB.MNRB_UI.pipeline_Editor_UI.pipeline_Editor_Scene as PipelineEditorScene #type: ignore
importlib.reload(PipelineEditorScene)

import MNRB.MNRB_UI.pipeline_Editor_UI.pipeline_Editor_Widget as PipelineEditorWidget #type: ignore
importlib.reload(PipelineEditorWidget)

import MNRB.MNRB_UI.mnrb_pipelineEditorTab as PipelineEditorTab #type: ignore
importlib.reload(PipelineEditorTab)

import MNRB.MNRB_UI.mnrb_editor as mnrb_editor #type: ignore
importlib.reload(mnrb_editor)

print("--- Registry after reload ---")
print("PIPELINE_STEPS:", PipelineEditorConf.PIPELINE_STEPS)
for code, cls in PipelineEditorConf.PIPELINE_STEPS.items():
    print(" code", code, "->", cls.__module__, cls.__name__, "properties class:", cls.Node_Properties_Class.__name__)
print("------------------------------")

# close every currently-open MNRB editor window and open a fresh one - reloading
# modules does not change objects that were already constructed from old classes
closed_count = 0
for widget in QApplication.topLevelWidgets():
    if isinstance(widget, mnrb_editor.mnrb_Editor):
        widget.hide()
        widget.deleteLater()
        closed_count += 1
print("Closed %d existing MNRB editor window(s)" % closed_count)

new_editor = mnrb_editor.mnrb_Editor()
new_editor.show()
print("Opened a fresh MNRB editor window. Add a brand new Output Path step on the")
print("Pipeline tab (old ones loaded from a saved file were built with whatever")
print("class was registered at save time) and check its properties panel.")
