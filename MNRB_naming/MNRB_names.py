
class MNRB_Side():
    def __init__(self, side_name, side_prefix) -> None:
        self.side = side_name
        self.prefix = side_prefix

class MNRB_buildSteps():
    static = "Build Static"
    component = "Build Component"
    connected = "Build Connected"

class MNRB_Names():
    left = MNRB_Side("left", "L_")
    right = MNRB_Side("right", "R_")
    middle = MNRB_Side("middle", "M_")

    build_step = MNRB_buildSteps()

    component_id_attribute_name = "MNRB_Component_ID"

    guide_suffix = "_guide"
    rig_suffix = "_rig"
    component_suffix = "_cmpnt"
    input_hierarchy_suffix = "_input_hrc"
    output_hierarchy_suffix = "_output_hrc"
    system_hierarchy_suffix = "_system_hrc"
    control_hierarchy_suffix = "_control_hrc"

    guide_hierarchy_suffix = "_guides_hrc"
    guide_component_hierarchy_suffix = "_cmpntGuides_hrc"
    rig_hierarchy_suffix = "_rig_hrc"

    rig_hierarchy_component_suffix = "_components_hrc"
    rig_hierarchy_skeleton_suffix = "_skeleton_hrc"
    rig_hierarchy_geometry_suffix = "_geometry_hrc"
    rig_hierarchy_shapes_suffix ="_shapes_hrc"

    guide_material_suffix = "_lambert_MNRB_guide_material"
    guide_shader_suffix = "_lambert_MNRB_guide_shader_SG"
    guide_connector_suffix = "_connector"
    guide_up_suffix = "_up"
    guide_orient_suffix = "_orient"

    deform_suffix = "_def"
    control_suffix = "_ctrl"
    output_suffix = "_srtOut"
    input_suffix = "_srtIn"

    