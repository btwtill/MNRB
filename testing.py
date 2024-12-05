import importlib

import MNRB.MNRB_Nodes.node_Editor_conf as NodeEditorConf
importlib.reload(NodeEditorConf)

import MNRB.MNRB_naming.MNRB_names as MNRBNaming
importlib.reload(MNRBNaming)

import MNRB.MNRB_Nodes.Nodes.__init__ as Init
importlib.reload(Init)

import MNRB.global_variables as GlobalVar
importlib.reload(GlobalVar)

import MNRB.MNRB_colors.colors as MNRBColors
importlib.reload(MNRBColors)

import MNRB.MNRB_Nodes.property_UI_GraphicComponents.side_button as MNRBSideButton
importlib.reload(MNRBSideButton)

import MNRB.MNRB_Scene.virtual_hierarchy_object as MNRB_VirtualHierarchyObject
importlib.reload(MNRB_VirtualHierarchyObject)

import MNRB.MNRB_Scene.virtual_hierarchy as MNRB_Virtual_Hierarchy
importlib.reload(MNRB_Virtual_Hierarchy)

import MNRB.MNRB_Nodes.Nodes.base_component as MNRB_Base_Component_Node
importlib.reload(MNRB_Base_Component_Node)

import MNRB.MNRB_Nodes.mnrb_node_base as MNRBNodeBase
importlib.reload(MNRBNodeBase)

import MNRB.MNRB_cmds_wrapper.cmds_wrapper as MayaCommands
importlib.reload(MayaCommands)

import MNRB.MNRB_UI.mnrb_editor as mnrb_editor
importlib.reload(mnrb_editor)

import MNRB.MNRB_UI.mnrb_ui_utils as utils
importlib.reload(utils)

import MNRB.MNRB_UI.mnrb_nodeEditorTab as NodeEditorTab
importlib.reload(NodeEditorTab)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Widget as NodeEditorWidget
importlib.reload(NodeEditorWidget)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Serializable as NodeEditorSerializable
importlib.reload(NodeEditorSerializable)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Scene as NodeEditorScene
importlib.reload(NodeEditorScene)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node as NodeEditorNode
importlib.reload(NodeEditorNode)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket as NodeEditorSocket
importlib.reload(NodeEditorSocket)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge as NodeEditorEdge
importlib.reload(NodeEditorEdge)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_DragEdge as NodeEditorDragEdge
importlib.reload(NodeEditorDragEdge)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Cutline as NodeEditorCutline
importlib.reload(NodeEditorCutline)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_SceneHistory as NodeEditorSceneHistory
importlib.reload(NodeEditorSceneHistory)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Clipboard as NodeEditorSceneClipboard
importlib.reload(NodeEditorSceneClipboard)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_DragNodeList as NodeEditorDragNodeList
importlib.reload(NodeEditorDragNodeList)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_PropertiesWidget as NodeEditorPropertiesWidget
importlib.reload(NodeEditorPropertiesWidget)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_NodeProperties as NodeEditorNodeProperties
importlib.reload(NodeEditorNodeProperties)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_SceneProperties as NodeEditorSceneProperties
importlib.reload(NodeEditorSceneProperties)

import MNRB.MNRB_UI.node_Editor_UI.node_Editor_EdgeProperties as NodeEditorEdgeProperties
importlib.reload(NodeEditorEdgeProperties)

import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicScene as NodeEditorGraphicsScene
importlib.reload(NodeEditorGraphicsScene)

import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicView as NodeEditorGraphicsView
importlib.reload(NodeEditorGraphicsView)

import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicNode as NodeEditorGraphicsNode
importlib.reload(NodeEditorGraphicsNode)

import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicContent as NodeEditorGraphicContent
importlib.reload(NodeEditorGraphicContent)

import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicSocket as NodeEditorGraphicSocket 
importlib.reload(NodeEditorGraphicSocket)

import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdgePath as NodeEditorGraphicEdgePath
importlib.reload(NodeEditorGraphicEdgePath)

import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge as NodeEditorGraphicEdge
importlib.reload(NodeEditorGraphicEdge)

import MNRB.MNRB_UI.node_Editor_Exceptions.node_Editor_FileException as NodeEditorInvalidFile
importlib.reload(NodeEditorInvalidFile)

import MNRB.MNRB_UI.node_Editor_Exceptions.node_Editor_RegistrationException as NodeEditorRegistrationException
importlib.reload(NodeEditorRegistrationException)

import MNRB.MNRB_Guides.locator_guide_shape as MNRBLocatorGuide
importlib.reload(MNRBLocatorGuide)

import MNRB.MNRB_Guides.nurbs_shpere_guide_shape as MNRBNurbsSphereGuide
importlib.reload(MNRBNurbsSphereGuide)

import MNRB.MNRB_Guides.guide as MNRBGuide
importlib.reload(MNRBGuide)

import MNRB.MNRB_UI.preferences_UI.preferences_widget as MNRBPreferences 
importlib.reload(MNRBPreferences)

newEditor = mnrb_editor.mnrb_Editor()

newEditor.show()