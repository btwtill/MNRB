
def open():
    """This function is to open the the tools UI"""
    from PySide2.QtWidgets import QApplication, QMainWindow #type: ignore
    from MNRB.MNRB_UI import mnrb_editor #type: ignore

    def get_active_main_window():
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMainWindow) and widget.isVisible():
                return widget
        return None

    if get_active_main_window() is None:
        newEditor = mnrb_editor.mnrb_Editor()
        newEditor.show()

def reloadMNRBModules():
    print("Reloading MNRB Shelf and Modules............")
    import importlib

    import MNRB.MNRB_Nodes.node_Editor_conf as NodeEditorConf
    importlib.reload(NodeEditorConf)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_SocketTypes as MNRBSocketTypes
    importlib.reload(MNRBSocketTypes)

    import MNRB.MNRB_Naming.MNRB_names as MNRBNaming
    importlib.reload(MNRBNaming)

    import MNRB.MNRB_Nodes.Nodes.__init__ as Init
    importlib.reload(Init)

    import MNRB.global_variables as GlobalVar
    importlib.reload(GlobalVar)

    import MNRB.MNRB_Colors.colors as MNRBColors
    importlib.reload(MNRBColors)

    import MNRB.MNRB_Nodes.property_UI_GraphicComponents.side_button as MNRBSideButton
    importlib.reload(MNRBSideButton)

    import MNRB.MNRB_Nodes.property_UI_GraphicComponents.receit_widget as MNRBReceitWidget
    importlib.reload(MNRBReceitWidget)

    import MNRB.MNRB_Nodes.property_UI_GraphicComponents.seperator_widget as MNRB_SeparatorWidget
    importlib.reload(MNRB_SeparatorWidget)

    import MNRB.MNRB_Scene.virtual_hierarchy_object as MNRB_VirtualHierarchyObject
    importlib.reload(MNRB_VirtualHierarchyObject)

    import MNRB.MNRB_Scene.virtual_hierarchy as MNRB_Virtual_Hierarchy
    importlib.reload(MNRB_Virtual_Hierarchy)

    import MNRB.MNRB_Nodes.mnrb_node_template as MNRBNodeTemplate
    importlib.reload(MNRBNodeTemplate)

    import MNRB.MNRB_Nodes.Nodes.base_component as MNRB_Base_Component_Node
    importlib.reload(MNRB_Base_Component_Node)

    import MNRB.MNRB_Nodes.Nodes.single_deform_component as MNRB_SingleDeform_Component_Node
    importlib.reload(MNRB_SingleDeform_Component_Node)

    import MNRB.MNRB_Nodes.Nodes.multi_deform_component as MNRB_MultiDeformComponent_Node
    importlib.reload(MNRB_MultiDeformComponent_Node)

    import MNRB.MNRB_Nodes.mnrb_node_base as MNRBNodeBase
    importlib.reload(MNRBNodeBase)

    import MNRB.MNRB_cmds_wrapper.cmds_wrapper as MayaCommands
    importlib.reload(MayaCommands)

    import MNRB.MNRB_cmds_wrapper.matrix_functions as MatrixFunctions
    importlib.reload(MatrixFunctions)

    import MNRB.MNRB_cmds_wrapper.transform_functions as TransformFunctions
    importlib.reload(TransformFunctions)

    import MNRB.MNRB_UI.mnrb_editor as mnrb_editor
    importlib.reload(mnrb_editor)

    import MNRB.MNRB_UI.mnrb_ui_utils as utils
    importlib.reload(utils)

    import MNRB.MNRB_UI.UI_GraphicComponents.triangleWidget as TriangleWidget
    importlib.reload(TriangleWidget)

    import MNRB.MNRB_Guides.MNRB_Guide_Connector.guide_connector as MNRBGuideConnector
    importlib.reload(MNRBGuideConnector)

    import MNRB.MNRB_UI.mnrb_nodeEditorTab as NodeEditorTab
    importlib.reload(NodeEditorTab)

    import MNRB.MNRB_UI.mnrb_skinningEditorTab as SkinningEditorTab
    importlib.reload(SkinningEditorTab)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_multiEditPropertiesWidget as MNRBMultiEditWidget 
    importlib.reload(MNRBMultiEditWidget)

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

    import MNRB.MNRB_UI.UI_GraphicComponents.list_group_item as ListGroupItem
    importlib.reload(ListGroupItem)

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

    #Skining Editor
    import MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_DeformList as SkinningEditorDeformList
    importlib.reload(SkinningEditorDeformList)

    import MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_Toolbar as SkinningEditorToolbar
    importlib.reload(SkinningEditorToolbar)

    #Shapes
    import MNRB.MNRB_Guides.MNRB_Guide_Shapes.locator_guide_shape as MNRBLocatorGuide
    importlib.reload(MNRBLocatorGuide)

    import MNRB.MNRB_Guides.MNRB_Orientation_Shapes.locator_orient_guide_shape as MNRBLocatorGuideOrient
    importlib.reload(MNRBLocatorGuideOrient)

    import MNRB.MNRB_Guides.MNRB_Up_Shapes.locator_up_guide_shape as MNRBLocatorGuideUp
    importlib.reload(MNRBLocatorGuideUp)

    import MNRB.MNRB_Deform.deform as MNRBDeform
    importlib.reload(MNRBDeform)

    import MNRB.MNRB_Guides.MNRB_Guide_Shapes.nurbs_shpere_guide_shape as MNRBNurbsSphereGuide
    importlib.reload(MNRBNurbsSphereGuide)

    import MNRB.MNRB_Guides.MNRB_Orientation_Shapes.nurbs_orient_guide_shape as MNRBNurbsGuideOrient
    importlib.reload(MNRBNurbsGuideOrient)

    import MNRB.MNRB_Guides.MNRB_Up_Shapes.nurbs_up_guide_shape as MNRBNurbsGuideUp
    importlib.reload(MNRBNurbsGuideUp)

    import MNRB.MNRB_Guides.guide as MNRBGuide
    importlib.reload(MNRBGuide)

    import MNRB.MNRB_Controls.control as MNRBControl
    importlib.reload(MNRBControl)

    import MNRB.MNRB_Controls.control_shape as MNRBControl_shape
    importlib.reload(MNRBControl_shape)

    import MNRB.MNRB_UI.preferences_UI.preferences_widget as MNRBPreferences 
    importlib.reload(MNRBPreferences)
