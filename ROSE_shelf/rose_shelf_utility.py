import importlib
import os
from MNRB.ROSE_shelf import rose_shelf_base #type: ignore
importlib.reload(rose_shelf_base)

import MNRB.ROSE_shelf.module_loading as module_loading #type: ignore
importlib.reload(module_loading)

ICON_DIRECTORY = os.path.join(os.path.dirname(__file__), "icons")

class loadROSEShelf(rose_shelf_base._shelf):
    def build(self):

        #reload Shelf
        self.addButton(label="", icon=ICON_DIRECTORY + "/reload.png", command=module_loading.reloadROSEModules)

        self.addButton(label="", icon=ICON_DIRECTORY + "/rose_editor.png", command=module_loading.open)

        # Separator
        self.addButton(label="", icon=ICON_DIRECTORY + "/sep.png", command="print('Separator DUH!!')")
