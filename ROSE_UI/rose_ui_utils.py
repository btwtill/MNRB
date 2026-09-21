from PySide6 import QtWidgets # type: ignore
from shiboken6 import wrapInstance # type: ignore
import maya.OpenMayaUI as omui # type: ignore

def getMayaWindow():
    main_window_pointer =  omui.MQtUtil.mainWindow()

    return wrapInstance(int(main_window_pointer), QtWidgets.QWidget)

def findIndexByAttribute(obj_list, attribute_value):
    for index, obj in enumerate(obj_list):
        if obj.id == attribute_value:
            #print("ID", obj.id, " of Object:: ", obj, " matches ID: ", attribute_value)
            #print("Index to be returned: ", index)
            return index
    return -1

def findProjectGraphFile(folder_path):
    """The graph .json inside one tab's project folder, or None if there isn't one.

    Every tab used to take os.listdir(folder)[0]. That order is arbitrary, and
    the skinning folder gains a `weights/` subdirectory the moment any weights
    are stored - which listed ahead of the graph, so the tab tried to open a
    directory as its graph, hit IsADirectoryError, swallowed it, and came up
    empty. The data was still on disk, one save away from being overwritten by
    that empty state.
    """
    import os

    if not os.path.isdir(folder_path):
        return None

    candidates = [name for name in sorted(os.listdir(folder_path))
                  if name.endswith(".json")
                  and os.path.isfile(os.path.join(folder_path, name))]

    if not candidates:
        return None

    #a project writes one graph per tab folder; prefer the conventional name if
    #anything else ever ends up alongside it
    for name in candidates:
        if name.endswith("_graph.json"):
            return os.path.join(folder_path, name)

    return os.path.join(folder_path, candidates[0])
