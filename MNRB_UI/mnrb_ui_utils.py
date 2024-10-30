from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui

def get_maya_window():
    main_window_pointer =  omui.MQtUtil.mainWindow()

    return wrapInstance(int(main_window_pointer), QtWidgets.QWidget)