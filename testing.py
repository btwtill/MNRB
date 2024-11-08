import importlib
import MNRB.MNRB_UI.mnrb_editor as mnrb_editor
import MNRB.MNRB_UI.mnrb_ui_utils as utils
import MNRB.MNRB_UI.mnrb_nodeEditorTab as nodeEditorTab

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Widget as nodeEditorWidget
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable as nodeEditorSerializable
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Scene as nodeEditorScene
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node as nodeEditorNode

import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicScene as nodeEditorGraphicsScene
import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicView as nodeEditorGraphicsView
import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGrpahicNode as nodeEditorGraphicsNode
import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicContent as nodeEditorGraphicContent


importlib.reload(mnrb_editor)
importlib.reload(utils)
importlib.reload(nodeEditorTab)

importlib.reload(nodeEditorWidget)
importlib.reload(nodeEditorSerializable)
importlib.reload(nodeEditorScene)
importlib.reload(nodeEditorNode)

importlib.reload(nodeEditorGraphicsScene)
importlib.reload(nodeEditorGraphicsView)
importlib.reload(nodeEditorGraphicsNode)
importlib.reload(nodeEditorGraphicContent)

newEditor = mnrb_editor.mnrb_Editor()

newEditor.show()