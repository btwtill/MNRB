import importlib
import MNRB.MNRB_UI.mnrb_editor as mnrb_editor
import MNRB.MNRB_UI.mnrb_ui_utils as utils
import MNRB.MNRB_UI.mnrb_nodeEditorTab as nodeEditorTab

importlib.reload(mnrb_editor)
importlib.reload(utils)
importlib.reload(nodeEditorTab)

newEditor = mnrb_editor.mnrb_Editor()

newEditor.show()