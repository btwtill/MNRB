"""Whether library control shapes are on, as the pipeline decides it.

Kept apart from the step itself (steps/control_shape_step.py) so the editor can
ask without importing a step module: steps are loaded by the pipeline registry,
which imports every step, and importing one directly first is a circular import.
"""

OPERATIONCODE_CONTROLSHAPESTEP = 4


def areControlShapesEnabled(pipeline_scene):
    """False only if the pipeline has a Control Shapes step and it is disabled.

    No step at all means on: a project that never set up a pipeline should still
    get the shapes it assigned."""
    if pipeline_scene is None:
        return True

    for node in pipeline_scene.nodes:
        #by operation code, not isinstance: a shelf Reload recreates the class, and
        #a node made before it would no longer count as one
        if getattr(node, "operation_code", None) == OPERATIONCODE_CONTROLSHAPESTEP \
                and node.properties.is_disabled:
            return False
    return True
