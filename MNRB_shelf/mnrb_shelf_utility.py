import importlib
import maya.utils #type: ignore
import  MNRB.MNRB_UI.mnrb_editor as mnrb_editor #type: ignore
from PySide2.QtWidgets import QApplication, QMainWindow #type: ignore

import MNRB.module_loading as module_loading #type: ignore
importlib.reload(module_loading)


def openMNRBEditor():
    def get_active_main_window():
        # Iterate through all top-level widgets
        for widget in QApplication.topLevelWidgets():
            # Check if the widget is a QMainWindow and is visible
            if isinstance(widget, QMainWindow) and widget.isVisible():
                return widget
        return None

    if get_active_main_window() is None:
        newEditor = mnrb_editor.mnrb_Editor()
        newEditor.show()

def reloadShelf():
    module_loading.reloadMNRBModules()

    import importlib
    from MNRB.MNRB_shelf import mnrb_shelf #type: ignore
    importlib.reload(mnrb_shelf)

    def load_userMNRB_shelf():
        mnrb_shelf.loadMNRBShelf(name ="MNRB_shelf")

    maya.utils.executeDeferred("load_userMNRB_shelf()")