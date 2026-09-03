
def open():
    """This function is to open the the tools UI"""
    from PySide6.QtWidgets import QApplication #type: ignore
    from MNRB.ROSE_UI import rose_editor #type: ignore

    def get_active_editor_window():
        #was previously isinstance(widget, QMainWindow), which matches ANY visible
        #top-level QMainWindow in the whole Qt application, not specifically ROSE's
        #own editor - too loose to reliably prevent duplicate editor windows.
        #
        #also can't use isinstance(widget, rose_editor.rose_Editor) here - every
        #shelf Reload does importlib.reload(rose_editor), which rebuilds rose_Editor
        #as a NEW class object under the same name. A window opened before that
        #reload is an instance of the OLD class object, so isinstance against the
        #post-reload class silently returns False and the dedup check misses it -
        #comparing by name/module string survives the reload since that identity
        #doesn't change even when the class object does
        for widget in QApplication.topLevelWidgets():
            widget_class = type(widget)
            if (widget_class.__name__ == "rose_Editor"
                    and widget_class.__module__ == rose_editor.rose_Editor.__module__
                    and widget.isVisible()):
                return widget
        return None

    existing_editor = get_active_editor_window()
    if existing_editor is not None:
        existing_editor.raise_()
        existing_editor.activateWindow()
        return

    newEditor = rose_editor.rose_Editor()
    newEditor.show()

def reloadROSEModules():
    print("Reloading ROSE Shelf and Modules............")
    import importlib

    import MNRB.ROSE_Nodes.node_Editor_conf as NodeEditorConf #type: ignore
    importlib.reload(NodeEditorConf)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_SocketTypes as ROSESocketTypes #type: ignore
    importlib.reload(ROSESocketTypes)

    import MNRB.ROSE_naming.ROSE_names as ROSENaming #type: ignore
    importlib.reload(ROSENaming)

    import MNRB.ROSE_Nodes.Nodes.__init__ as Init #type: ignore
    importlib.reload(Init)

    import MNRB.global_variables as GlobalVar #type: ignore
    importlib.reload(GlobalVar)

    import MNRB.ROSE_colors.colors as ROSEColors #type: ignore
    importlib.reload(ROSEColors)

    import MNRB.ROSE_Nodes.property_UI_GraphicComponents.side_button as ROSESideButton #type: ignore
    importlib.reload(ROSESideButton)

    import MNRB.ROSE_Nodes.property_UI_GraphicComponents.receit_widget as ROSEReceitWidget #type: ignore
    importlib.reload(ROSEReceitWidget)
 
    import MNRB.ROSE_Nodes.property_UI_GraphicComponents.seperator_widget as ROSE_SeparatorWidget #type: ignore
    importlib.reload(ROSE_SeparatorWidget)

    import MNRB.ROSE_Scene.virtual_hierarchy_object as ROSE_VirtualHierarchyObject #type: ignore
    importlib.reload(ROSE_VirtualHierarchyObject)

    import MNRB.ROSE_Scene.virtual_hierarchy as ROSE_Virtual_Hierarchy #type: ignore
    importlib.reload(ROSE_Virtual_Hierarchy)

    import MNRB.ROSE_Nodes.rose_node_template as ROSENodeTemplate #type: ignore
    importlib.reload(ROSENodeTemplate)

    import MNRB.ROSE_Nodes.Nodes.base_component as ROSE_Base_Component_Node #type: ignore
    importlib.reload(ROSE_Base_Component_Node)

    import MNRB.ROSE_Nodes.Nodes.single_deform_component as ROSE_SingleDeform_Component_Node #type: ignore
    importlib.reload(ROSE_SingleDeform_Component_Node)

    import MNRB.ROSE_Nodes.Nodes.multi_deform_component as ROSE_MultiDeformComponent_Node #type: ignore
    importlib.reload(ROSE_MultiDeformComponent_Node)

    import MNRB.ROSE_Nodes.Nodes.simple_ik_component as ROSE_SimpleIKComponent_Node #type: ignore
    importlib.reload(ROSE_SimpleIKComponent_Node)

    import MNRB.ROSE_Nodes.rose_node_base as ROSENodeBase #type: ignore
    importlib.reload(ROSENodeBase)

    import MNRB.ROSE_cmds_wrapper.cmds_wrapper as MayaCommands #type: ignore
    importlib.reload(MayaCommands)

    import MNRB.ROSE_cmds_wrapper.matrix_functions as MatrixFunctions #type: ignore 
    importlib.reload(MatrixFunctions)

    import MNRB.ROSE_cmds_wrapper.transform_functions as TransformFunctions #type: ignore
    importlib.reload(TransformFunctions)

    import MNRB.ROSE_UI.rose_ui_utils as utils #type: ignore
    importlib.reload(utils)

    import MNRB.ROSE_UI.UI_GraphicComponents.triangleWidget as TriangleWidget #type: ignore
    importlib.reload(TriangleWidget)

    import MNRB.ROSE_Guides.ROSE_Guide_Connector.guide_connector as ROSEGuideConnector #type: ignore
    importlib.reload(ROSEGuideConnector)

    import MNRB.ROSE_UI.rose_nodeEditorTab as NodeEditorTab #type: ignore
    importlib.reload(NodeEditorTab)

    #Skinning Editor - must reload before rose_skinningEditorTab below, since that
    #module imports all of these at its own module level and would otherwise keep
    #holding stale class references across repeated reloads
    import MNRB.ROSE_UI.skinning_Editor_UI.skinning_Editor_Cluster as SkinningEditorCluster #type: ignore
    importlib.reload(SkinningEditorCluster)

    import MNRB.ROSE_UI.skinning_Editor_UI.skinning_Editor_ClusterComponentWidget as SkinningEditorClusterComponentWidget #type: ignore
    importlib.reload(SkinningEditorClusterComponentWidget)

    import MNRB.ROSE_UI.skinning_Editor_UI.skinning_Editor_DeformList as SkinningEditorDeformList #type: ignore
    importlib.reload(SkinningEditorDeformList)

    import MNRB.ROSE_UI.skinning_Editor_UI.skinning_Editor_ClusterList as SkinningEditorClusterList #type: ignore
    importlib.reload(SkinningEditorClusterList)

    import MNRB.ROSE_UI.skinning_Editor_UI.skinning_Editor_Toolbar as SkinningEditorToolbar #type: ignore
    importlib.reload(SkinningEditorToolbar)

    import MNRB.ROSE_UI.rose_skinningEditorTab as SkinningEditorTab #type: ignore
    importlib.reload(SkinningEditorTab)

    #Pipeline Editor - same reload-order requirement as the Skinning Editor block
    #above: dependencies before the modules that import them
    import MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_StepGraphicNode as PipelineEditorStepGraphicNode #type: ignore
    importlib.reload(PipelineEditorStepGraphicNode)

    import MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_StepNode as PipelineEditorStepNode #type: ignore
    importlib.reload(PipelineEditorStepNode)

    import MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_conf as PipelineEditorConf #type: ignore
    importlib.reload(PipelineEditorConf)

    import MNRB.ROSE_UI.pipeline_Editor_UI.steps.control_rig_step as ControlRigStep #type: ignore
    importlib.reload(ControlRigStep)

    import MNRB.ROSE_UI.pipeline_Editor_UI.steps.output_path_step as OutputPathStep #type: ignore
    importlib.reload(OutputPathStep)

    import MNRB.ROSE_UI.pipeline_Editor_UI.steps.skinning_step as SkinningStep #type: ignore
    importlib.reload(SkinningStep)

    import MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_SceneProperties as PipelineEditorSceneProperties #type: ignore
    importlib.reload(PipelineEditorSceneProperties)

    import MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_Scene as PipelineEditorScene #type: ignore
    importlib.reload(PipelineEditorScene)

    import MNRB.ROSE_UI.pipeline_Editor_UI.pipeline_Editor_Widget as PipelineEditorWidget #type: ignore
    importlib.reload(PipelineEditorWidget)

    import MNRB.ROSE_UI.rose_pipelineEditorTab as PipelineEditorTab #type: ignore
    importlib.reload(PipelineEditorTab)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_multiEditPropertiesWidget as ROSEMultiEditWidget  #type: ignore
    importlib.reload(ROSEMultiEditWidget)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_Widget as NodeEditorWidget #type: ignore
    importlib.reload(NodeEditorWidget)

    import MNRB.ROSE_Data.rose_Editor_Serializable as NodeEditorSerializable #type: ignore
    importlib.reload(NodeEditorSerializable)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_Scene as NodeEditorScene #type: ignore
    importlib.reload(NodeEditorScene)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_Node as NodeEditorNode #type: ignore
    importlib.reload(NodeEditorNode)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_Socket as NodeEditorSocket #type: ignore
    importlib.reload(NodeEditorSocket)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_Edge as NodeEditorEdge #type: ignore
    importlib.reload(NodeEditorEdge)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_DragEdge as NodeEditorDragEdge #type: ignore
    importlib.reload(NodeEditorDragEdge)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_Cutline as NodeEditorCutline #type: ignore
    importlib.reload(NodeEditorCutline)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_SceneHistory as NodeEditorSceneHistory #type: ignore
    importlib.reload(NodeEditorSceneHistory)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_Clipboard as NodeEditorSceneClipboard #type: ignore
    importlib.reload(NodeEditorSceneClipboard)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_DragNodeList as NodeEditorDragNodeList #type: ignore
    importlib.reload(NodeEditorDragNodeList)

    import MNRB.ROSE_UI.UI_GraphicComponents.list_group_item as ListGroupItem #type: ignore
    importlib.reload(ListGroupItem)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_PropertiesWidget as NodeEditorPropertiesWidget #type: ignore
    importlib.reload(NodeEditorPropertiesWidget)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_NodeProperties as NodeEditorNodeProperties #type: ignore
    importlib.reload(NodeEditorNodeProperties)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_SceneProperties as NodeEditorSceneProperties #type: ignore
    importlib.reload(NodeEditorSceneProperties)

    import MNRB.ROSE_UI.node_Editor_UI.node_Editor_EdgeProperties as NodeEditorEdgeProperties #type: ignore
    importlib.reload(NodeEditorEdgeProperties)

    import MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicScene as NodeEditorGraphicsScene #type: ignore
    importlib.reload(NodeEditorGraphicsScene)

    import MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicView as NodeEditorGraphicsView #type: ignore
    importlib.reload(NodeEditorGraphicsView)

    import MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicNode as NodeEditorGraphicsNode #type: ignore
    importlib.reload(NodeEditorGraphicsNode)

    import MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicContent as NodeEditorGraphicContent #type: ignore
    importlib.reload(NodeEditorGraphicContent)

    import MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicSocket as NodeEditorGraphicSocket  #type: ignore
    importlib.reload(NodeEditorGraphicSocket)

    import MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdgePath as NodeEditorGraphicEdgePath #type: ignore
    importlib.reload(NodeEditorGraphicEdgePath)

    import MNRB.ROSE_UI.node_Editor_GraphicComponents.node_Editor_QGraphicEdge as NodeEditorGraphicEdge #type: ignore
    importlib.reload(NodeEditorGraphicEdge)

    import MNRB.ROSE_UI.node_Editor_Exceptions.node_Editor_FileException as NodeEditorInvalidFile #type: ignore
    importlib.reload(NodeEditorInvalidFile)

    import MNRB.ROSE_UI.node_Editor_Exceptions.node_Editor_RegistrationException as NodeEditorRegistrationException #type: ignore
    importlib.reload(NodeEditorRegistrationException)

    #Shapes
    import MNRB.ROSE_Guides.ROSE_Guide_Shapes.locator_guide_shape as ROSELocatorGuide #type: ignore
    importlib.reload(ROSELocatorGuide)

    import MNRB.ROSE_Guides.ROSE_Orientation_Shapes.locator_orient_guide_shape as ROSELocatorGuideOrient #type: ignore
    importlib.reload(ROSELocatorGuideOrient)

    import MNRB.ROSE_Guides.ROSE_Up_Shapes.locator_up_guide_shape as ROSELocatorGuideUp #type: ignore
    importlib.reload(ROSELocatorGuideUp)

    import MNRB.ROSE_Deform.deform as ROSEDeform #type: ignore
    importlib.reload(ROSEDeform)

    import MNRB.ROSE_Guides.ROSE_Guide_Shapes.nurbs_shpere_guide_shape as ROSENurbsSphereGuide #type: ignore
    importlib.reload(ROSENurbsSphereGuide)

    import MNRB.ROSE_Guides.ROSE_Orientation_Shapes.nurbs_orient_guide_shape as ROSENurbsGuideOrient #type: ignore
    importlib.reload(ROSENurbsGuideOrient)

    import MNRB.ROSE_Guides.ROSE_Up_Shapes.nurbs_up_guide_shape as ROSENurbsGuideUp #type: ignore
    importlib.reload(ROSENurbsGuideUp)

    import MNRB.ROSE_Guides.guide as ROSEGuide #type: ignore
    importlib.reload(ROSEGuide)

    import MNRB.ROSE_Controls.control as ROSEControl #type: ignore
    importlib.reload(ROSEControl)

    import MNRB.ROSE_Controls.control_shape as ROSEControl_shape #type: ignore
    importlib.reload(ROSEControl_shape)

    import MNRB.ROSE_UI.preferences_UI.preferences_widget as ROSEPreferences  #type: ignore
    importlib.reload(ROSEPreferences)

    #rose_editor.py imports rose_nodeEditorTab/rose_skinningEditorTab/rose_pipelineEditorTab/
    #ROSEPreferences directly at its own module level, so it has to reload last -
    #this used to reload first (before any of those), meaning it could silently
    #hold stale references to all three tab classes on a second reload
    import MNRB.ROSE_UI.rose_editor as rose_editor #type: ignore
    importlib.reload(rose_editor)
