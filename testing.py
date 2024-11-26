import importlib
import MNRB.MNRB_Nodes.node_Editor_conf as NodeEditorConf 
import MNRB.MNRB_Nodes.Nodes.__init__ as Init

import MNRB.MNRB_Nodes.Nodes.base_component as MNRB_Base_Component_Node
import MNRB_Scene.scene_hirarchy as MNRB_Scene_Hirarchy
import MNRB.MNRB_cmds_wrapper.cmds_wrapper as MayaCommands

import MNRB.MNRB_UI.mnrb_editor as mnrb_editor
import MNRB.MNRB_UI.mnrb_ui_utils as utils
import MNRB.MNRB_UI.mnrb_nodeEditorTab as NodeEditorTab

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Widget as NodeEditorWidget
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable as NodeEditorSerializable
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Scene as NodeEditorScene
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node as NodeEditorNode
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket as NodeEditorSocket
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge as NodeEditorEdge
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_DragEdge as NodeEditorDragEdge
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Cutline as NodeEditorCutline
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_SceneHistory as NodeEditorSceneHistory
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Clipboard as NodeEditorSceneClipboard
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_DragNodeList as NodeEditorDragNodeList
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_PropertiesWidget as NodeEditorPropertiesWidget
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_NodeProperties as NodeEditorNodeProperties
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_SceneProperties as NodeEditorSceneProperties
import MNRB.MNRB_UI.node_Editor_UI.node_Editor_EdgeProperties as NodeEditorEdgeProperties

import MNRB.MNRB_Nodes.mnrb_node_base as MNRBNodeBase

import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicScene as NodeEditorGraphicsScene
import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicView as NodeEditorGraphicsView
import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicNode as NodeEditorGraphicsNode
import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicContent as NodeEditorGraphicContent
import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicSocket as NodeEditorGraphicSocket 
import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdgePath as NodeEditorGraphicEdgePath
import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge as NodeEditorGraphicEdge

import MNRB.MNRB_UI.node_Editor_Exceptions.node_Editor_FileException as NodeEditorInvalidFile
import MNRB.MNRB_UI.node_Editor_Exceptions.node_Editor_RegistrationException as NodeEditorRegistrationException

import MNRB.global_variables as GlobalVar

import MNRB.MNRB_Guides.guide as MNRBGuide

importlib.reload(NodeEditorConf)
importlib.reload(Init)

importlib.reload(MNRBNodeBase)
importlib.reload(MNRB_Scene_Hirarchy)
importlib.reload(MNRB_Base_Component_Node)

importlib.reload(MayaCommands)

importlib.reload(mnrb_editor)
importlib.reload(utils)
importlib.reload(NodeEditorTab)

importlib.reload(NodeEditorWidget)
importlib.reload(NodeEditorSerializable)
importlib.reload(NodeEditorScene)
importlib.reload(NodeEditorNode)
importlib.reload(NodeEditorSocket)
importlib.reload(NodeEditorEdge)
importlib.reload(NodeEditorDragEdge)
importlib.reload(NodeEditorCutline)
importlib.reload(NodeEditorSceneHistory)
importlib.reload(NodeEditorSceneClipboard)
importlib.reload(NodeEditorDragNodeList)
importlib.reload(NodeEditorPropertiesWidget)
importlib.reload(NodeEditorNodeProperties)
importlib.reload(NodeEditorSceneProperties)
importlib.reload(NodeEditorEdgeProperties)

importlib.reload(NodeEditorGraphicsScene)
importlib.reload(NodeEditorGraphicsView)
importlib.reload(NodeEditorGraphicsNode)
importlib.reload(NodeEditorGraphicContent)
importlib.reload(NodeEditorGraphicSocket)
importlib.reload(NodeEditorGraphicEdgePath)
importlib.reload(NodeEditorGraphicEdge)

importlib.reload(NodeEditorInvalidFile)
importlib.reload(NodeEditorRegistrationException)

importlib.reload(GlobalVar)

importlib.reload(MNRBGuide)

newEditor = mnrb_editor.mnrb_Editor()

newEditor.show()