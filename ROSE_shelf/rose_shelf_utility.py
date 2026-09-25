import importlib
import os
from MNRB.ROSE_shelf import rose_shelf_base #type: ignore
importlib.reload(rose_shelf_base)

import MNRB.ROSE_shelf.module_loading as module_loading #type: ignore
importlib.reload(module_loading)

ICON_DIRECTORY = os.path.join(os.path.dirname(__file__), "icons")

class loadROSEShelf(rose_shelf_base._shelf):
    def build(self):

        #reload Shelf.
        #
        #reloadROSEEditor rather than reloadROSEModules: reloading the modules on
        #its own cannot change a window that is already open, because every widget
        #on screen is an instance of the class as it was when the window was made.
        #This one recreates the editor on the same project so UI changes actually
        #show up - and leaves it alone if there is unsaved work.
        self.addButton(label="", icon=ICON_DIRECTORY + "/reload.png", command=module_loading.reloadROSEEditor)

        self.addButton(label="", icon=ICON_DIRECTORY + "/rose_editor.png", command=module_loading.open)

        # Separator
        self.addButton(label="", icon=ICON_DIRECTORY + "/sep.png", command="print('Separator DUH!!')")
