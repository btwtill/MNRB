
class MNRB_Side():
    def __init__(self, side_name, side_prefix) -> None:
        self.side = side_name
        self.prefix = side_prefix

class MNRB_Names():
    left = MNRB_Side("left", "L_")
    right = MNRB_Side("right", "R_")
    middle = MNRB_Side("middle", "M_")

    component_id_attribute_name = "MNRB_Component_ID"

    guide_suffix = "_guide"
    rig_suffix = "_rig"
    component_suffix = "_cmpnt"

    guide_hierarchy_suffix = "_guides_hrc"
    guide_component_hierarchy_suffix = "_cmpntGuides_hrc"
    rig_hierarchy_suffix = "_rig_hrc"

    rig_hierarchy_component_suffix = "_components_hrc"
    rig_hierarchy_skeleton_suffix = "_skeleton_hrc"
    rig_hierarchy_geometry_suffix = "_geometry_hrc"
    rig_hierarchy_shapes_suffix ="_shapes_hrc"

    guide_material_suffix = "_lambert_MNRB_guide_material"
    guide_shader_suffix = "_lambert_MNRB_guide_shader_SG"
