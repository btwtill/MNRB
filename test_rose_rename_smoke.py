"""
Smoke test for the MNRB -> ROSE rename: force-reloads the full module tree under
its new ROSE_* names, prints the node/pipeline-step registries so you can see
they're populated under the new names, closes any existing editor window, and
opens a fresh one.

Paste into Maya's Script Editor and run. Not part of the ROSE package - delete
once you've confirmed everything opens without errors.
"""

from PySide6.QtWidgets import QApplication #type: ignore

from MNRB.ROSE_shelf import rose_shelf_utility
import importlib
importlib.reload(rose_shelf_utility)

import MNRB.ROSE_shelf.module_loading as module_loading
importlib.reload(module_loading)
module_loading.reloadROSEModules()

import MNRB.ROSE_Nodes.node_Editor_conf as NodeEditorConf
print("--- Node registry (ROSE_NODES) ---")
for code, cls in NodeEditorConf.ROSE_NODES.items():
    print(" code", code, "->", cls.__module__, cls.__name__)

import MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_conf as PipelineEditorConf
print("--- Pipeline step registry (PIPELINE_STEPS) ---")
for code, cls in PipelineEditorConf.PIPELINE_STEPS.items():
    print(" code", code, "->", cls.__module__, cls.__name__)

import MNRB.ROSE_UI.rose_editor as rose_editor
importlib.reload(rose_editor)

closed_count = 0
for widget in QApplication.topLevelWidgets():
    if isinstance(widget, rose_editor.rose_Editor):
        widget.hide()
        widget.deleteLater()
        closed_count += 1
print("Closed %d existing editor window(s)" % closed_count)

new_editor = rose_editor.rose_Editor()
new_editor.show()
print("Opened a fresh ROSE Editor window - check the title bar reads 'ROSE Editor',")
print("open each of the three tabs, and confirm nothing printed a traceback above.")
