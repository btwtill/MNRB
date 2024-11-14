from PySide2 import QtWidgets # type: ignore
from shiboken2 import wrapInstance # type: ignore
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