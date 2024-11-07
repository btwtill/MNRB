from PySide2 import QtWidgets # type: ignore
from shiboken2 import wrapInstance # type: ignore
import maya.OpenMayaUI as omui # type: ignore

def get_maya_window():
    main_window_pointer =  omui.MQtUtil.mainWindow()

    return wrapInstance(int(main_window_pointer), QtWidgets.QWidget)