"""
Closes every currently-open MNRB editor window (leftover from repeated test-script
runs earlier this session), then opens exactly one fresh one.

Paste into Maya's Script Editor and run. Not part of the MNRB package - delete
once done. After this, use the shelf's own open/reload buttons going forward
rather than the other test_*.py scripts from earlier in this session - those were
one-off diagnostics for bugs that are now fixed.
"""

from PySide6.QtWidgets import QApplication #type: ignore
import MNRB.MNRB_UI.mnrb_editor as mnrb_editor #type: ignore

closed_count = 0
for widget in QApplication.topLevelWidgets():
    if isinstance(widget, mnrb_editor.mnrb_Editor):
        widget.hide()
        widget.deleteLater()
        closed_count += 1

print("Closed %d MNRB editor window(s)" % closed_count)

new_editor = mnrb_editor.mnrb_Editor()
new_editor.show()
print("Opened one fresh MNRB editor window.")
