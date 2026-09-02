
def open():
    """This function is to open the the tools UI"""
    from PySide6.QtWidgets import QApplication #type: ignore
    from MNRB.MNRB_UI import mnrb_editor #type: ignore

    def get_active_editor_window():
        #was previously isinstance(widget, QMainWindow), which matches ANY visible
        #top-level QMainWindow in the whole Qt application, not specifically MNRB's
        #own editor - too loose to reliably prevent duplicate editor windows
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, mnrb_editor.mnrb_Editor) and widget.isVisible():
                return widget
        return None

    existing_editor = get_active_editor_window()
    if existing_editor is not None:
        existing_editor.raise_()
        existing_editor.activateWindow()
        return

    newEditor = mnrb_editor.mnrb_Editor()
    newEditor.show()

def reloadMNRBModules():
    print("Reloading MNRB Shelf and Modules............")
    import importlib

    import MNRB.MNRB_Nodes.node_Editor_conf as NodeEditorConf #type: ignore
    importlib.reload(NodeEditorConf)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_SocketTypes as MNRBSocketTypes #type: ignore
    importlib.reload(MNRBSocketTypes)

    import MNRB.MNRB_naming.MNRB_names as MNRBNaming #type: ignore
    importlib.reload(MNRBNaming)

    import MNRB.MNRB_Nodes.Nodes.__init__ as Init #type: ignore
    importlib.reload(Init)

    import MNRB.global_variables as GlobalVar #type: ignore
    importlib.reload(GlobalVar)

    import MNRB.MNRB_colors.colors as MNRBColors #type: ignore
    importlib.reload(MNRBColors)

    import MNRB.MNRB_Nodes.property_UI_GraphicComponents.side_button as MNRBSideButton #type: ignore
    importlib.reload(MNRBSideButton)

    import MNRB.MNRB_Nodes.property_UI_GraphicComponents.receit_widget as MNRBReceitWidget #type: ignore
    importlib.reload(MNRBReceitWidget)
 
    import MNRB.MNRB_Nodes.property_UI_GraphicComponents.seperator_widget as MNRB_SeparatorWidget #type: ignore
    importlib.reload(MNRB_SeparatorWidget)

    import MNRB.MNRB_Scene.virtual_hierarchy_object as MNRB_VirtualHierarchyObject #type: ignore
    importlib.reload(MNRB_VirtualHierarchyObject)

    import MNRB.MNRB_Scene.virtual_hierarchy as MNRB_Virtual_Hierarchy #type: ignore
    importlib.reload(MNRB_Virtual_Hierarchy)

    import MNRB.MNRB_Nodes.mnrb_node_template as MNRBNodeTemplate #type: ignore
    importlib.reload(MNRBNodeTemplate)

    import MNRB.MNRB_Nodes.Nodes.base_component as MNRB_Base_Component_Node #type: ignore
    importlib.reload(MNRB_Base_Component_Node)

    import MNRB.MNRB_Nodes.Nodes.single_deform_component as MNRB_SingleDeform_Component_Node #type: ignore
    importlib.reload(MNRB_SingleDeform_Component_Node)

    import MNRB.MNRB_Nodes.Nodes.multi_deform_component as MNRB_MultiDeformComponent_Node #type: ignore
    importlib.reload(MNRB_MultiDeformComponent_Node)

    import MNRB.MNRB_Nodes.Nodes.simple_ik_component as MNRB_SimpleIKComponent_Node #type: ignore
    importlib.reload(MNRB_SimpleIKComponent_Node)

    import MNRB.MNRB_Nodes.mnrb_node_base as MNRBNodeBase #type: ignore
    importlib.reload(MNRBNodeBase)

    import MNRB.MNRB_cmds_wrapper.cmds_wrapper as MayaCommands #type: ignore
    importlib.reload(MayaCommands)

    import MNRB.MNRB_cmds_wrapper.matrix_functions as MatrixFunctions #type: ignore 
    importlib.reload(MatrixFunctions)

    import MNRB.MNRB_cmds_wrapper.transform_functions as TransformFunctions #type: ignore
    importlib.reload(TransformFunctions)

    import MNRB.MNRB_UI.mnrb_ui_utils as utils #type: ignore
    importlib.reload(utils)

    import MNRB.MNRB_UI.UI_GraphicComponents.triangleWidget as TriangleWidget #type: ignore
    importlib.reload(TriangleWidget)

    import MNRB.MNRB_Guides.MNRB_Guide_Connector.guide_connector as MNRBGuideConnector #type: ignore
    importlib.reload(MNRBGuideConnector)

    import MNRB.MNRB_UI.mnrb_nodeEditorTab as NodeEditorTab #type: ignore
    importlib.reload(NodeEditorTab)

    #Skinning Editor - must reload before mnrb_skinningEditorTab below, since that
    #module imports all of these at its own module level and would otherwise keep
    #holding stale class references across repeated reloads
    import MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_Cluster as SkinningEditorCluster #type: ignore
    importlib.reload(SkinningEditorCluster)

    import MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_ClusterComponentWidget as SkinningEditorClusterComponentWidget #type: ignore
    importlib.reload(SkinningEditorClusterComponentWidget)

    import MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_DeformList as SkinningEditorDeformList #type: ignore
    importlib.reload(SkinningEditorDeformList)

    import MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_ClusterList as SkinningEditorClusterList #type: ignore
    importlib.reload(SkinningEditorClusterList)

    import MNRB.MNRB_UI.skinning_Editor_UI.skinning_Editor_Toolbar as SkinningEditorToolbar #type: ignore
    importlib.reload(SkinningEditorToolbar)

    import MNRB.MNRB_UI.mnrb_skinningEditorTab as SkinningEditorTab #type: ignore
    importlib.reload(SkinningEditorTab)

    #Pipeline Editor - same reload-order requirement as the Skinning Editor block
    #above: dependencies before the modules that import them
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

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_multiEditPropertiesWidget as MNRBMultiEditWidget  #type: ignore
    importlib.reload(MNRBMultiEditWidget)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Widget as NodeEditorWidget #type: ignore
    importlib.reload(NodeEditorWidget)

    import MNRB.ROSE_Data.rose_Editor_Serializable as NodeEditorSerializable #type: ignore
    importlib.reload(NodeEditorSerializable)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Scene as NodeEditorScene #type: ignore
    importlib.reload(NodeEditorScene)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Node as NodeEditorNode #type: ignore
    importlib.reload(NodeEditorNode)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Socket as NodeEditorSocket #type: ignore
    importlib.reload(NodeEditorSocket)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Edge as NodeEditorEdge #type: ignore
    importlib.reload(NodeEditorEdge)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_DragEdge as NodeEditorDragEdge #type: ignore
    importlib.reload(NodeEditorDragEdge)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Cutline as NodeEditorCutline #type: ignore
    importlib.reload(NodeEditorCutline)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_SceneHistory as NodeEditorSceneHistory #type: ignore
    importlib.reload(NodeEditorSceneHistory)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_Clipboard as NodeEditorSceneClipboard #type: ignore
    importlib.reload(NodeEditorSceneClipboard)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_DragNodeList as NodeEditorDragNodeList #type: ignore
    importlib.reload(NodeEditorDragNodeList)

    import MNRB.MNRB_UI.UI_GraphicComponents.list_group_item as ListGroupItem #type: ignore
    importlib.reload(ListGroupItem)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_PropertiesWidget as NodeEditorPropertiesWidget #type: ignore
    importlib.reload(NodeEditorPropertiesWidget)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_NodeProperties as NodeEditorNodeProperties #type: ignore
    importlib.reload(NodeEditorNodeProperties)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_SceneProperties as NodeEditorSceneProperties #type: ignore
    importlib.reload(NodeEditorSceneProperties)

    import MNRB.MNRB_UI.node_Editor_UI.node_Editor_EdgeProperties as NodeEditorEdgeProperties #type: ignore
    importlib.reload(NodeEditorEdgeProperties)

    import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicScene as NodeEditorGraphicsScene #type: ignore
    importlib.reload(NodeEditorGraphicsScene)

    import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicView as NodeEditorGraphicsView #type: ignore
    importlib.reload(NodeEditorGraphicsView)

    import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicNode as NodeEditorGraphicsNode #type: ignore
    importlib.reload(NodeEditorGraphicsNode)

    import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicContent as NodeEditorGraphicContent #type: ignore
    importlib.reload(NodeEditorGraphicContent)

    import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicSocket as NodeEditorGraphicSocket  #type: ignore
    importlib.reload(NodeEditorGraphicSocket)

    import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdgePath as NodeEditorGraphicEdgePath #type: ignore
    importlib.reload(NodeEditorGraphicEdgePath)

    import MNRB.MNRB_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge as NodeEditorGraphicEdge #type: ignore
    importlib.reload(NodeEditorGraphicEdge)

    import MNRB.MNRB_UI.node_Editor_Exceptions.node_Editor_FileException as NodeEditorInvalidFile #type: ignore
    importlib.reload(NodeEditorInvalidFile)

    import MNRB.MNRB_UI.node_Editor_Exceptions.node_Editor_RegistrationException as NodeEditorRegistrationException #type: ignore
    importlib.reload(NodeEditorRegistrationException)

    #Shapes
    import MNRB.MNRB_Guides.MNRB_Guide_Shapes.locator_guide_shape as MNRBLocatorGuide #type: ignore
    importlib.reload(MNRBLocatorGuide)

    import MNRB.MNRB_Guides.MNRB_Orientation_Shapes.locator_orient_guide_shape as MNRBLocatorGuideOrient #type: ignore
    importlib.reload(MNRBLocatorGuideOrient)

    import MNRB.MNRB_Guides.MNRB_Up_Shapes.locator_up_guide_shape as MNRBLocatorGuideUp #type: ignore
    importlib.reload(MNRBLocatorGuideUp)

    import MNRB.MNRB_Deform.deform as MNRBDeform #type: ignore
    importlib.reload(MNRBDeform)

    import MNRB.MNRB_Guides.MNRB_Guide_Shapes.nurbs_shpere_guide_shape as MNRBNurbsSphereGuide #type: ignore
    importlib.reload(MNRBNurbsSphereGuide)

    import MNRB.MNRB_Guides.MNRB_Orientation_Shapes.nurbs_orient_guide_shape as MNRBNurbsGuideOrient #type: ignore
    importlib.reload(MNRBNurbsGuideOrient)

    import MNRB.MNRB_Guides.MNRB_Up_Shapes.nurbs_up_guide_shape as MNRBNurbsGuideUp #type: ignore
    importlib.reload(MNRBNurbsGuideUp)

    import MNRB.MNRB_Guides.guide as MNRBGuide #type: ignore
    importlib.reload(MNRBGuide)

    import MNRB.MNRB_Controls.control as MNRBControl #type: ignore
    importlib.reload(MNRBControl)

    import MNRB.MNRB_Controls.control_shape as MNRBControl_shape #type: ignore
    importlib.reload(MNRBControl_shape)

    import MNRB.MNRB_UI.preferences_UI.preferences_widget as MNRBPreferences  #type: ignore
    importlib.reload(MNRBPreferences)

    #mnrb_editor.py imports mnrb_nodeEditorTab/mnrb_skinningEditorTab/mnrb_pipelineEditorTab/
    #MNRBPreferences directly at its own module level, so it has to reload last -
    #this used to reload first (before any of those), meaning it could silently
    #hold stale references to all three tab classes on a second reload
    import MNRB.MNRB_UI.mnrb_editor as mnrb_editor #type: ignore
    importlib.reload(mnrb_editor)
