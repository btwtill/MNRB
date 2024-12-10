import os
import importlib
import MNRB.MNRB_shelf.mnrb_shelf_utility as mnrb_shelf_utility #type: ignore
importlib.reload(mnrb_shelf_utility)

from MNRB.MNRB_shelf.mnrb_shelf_base import _shelf #type: ignore

ICON_DIRECTORY = os.path.join(os.path.dirname(__file__), "icons")


class loadMNRBShelf(_shelf):
    def build(self):

        #reload Shelf
        self.addButton(label="", icon=ICON_DIRECTORY + "/reload.png", command=mnrb_shelf_utility.reloadShelf)
        
        #MNRB Editor Button
        self.addButton(label="", icon=ICON_DIRECTORY + "/mnrb_editor.png", command=mnrb_shelf_utility.openMNRBEditor)

        # Separator
        self.addButton(label="", icon=ICON_DIRECTORY + "/sep.png", command="print('Separator DUH!!')")
