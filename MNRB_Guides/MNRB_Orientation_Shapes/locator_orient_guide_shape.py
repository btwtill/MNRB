from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

class LocatorOrientGuideShape():
    def __init__(self, guide) -> None:
        self.guide = guide

    def draw(self):
        guide_shape = MC.createSpaceLocator(self.guide.position, self.guide.name_orient, self.guide.color.value)
        self.guide.name_orient = guide_shape

    def resize(self, size):
        MC.setLocatorLocalScale(self.guide.name_orient, size)

    def updateColor(self):
        MC.setObjectDisplayColor(self.guide.name_orient, self.guide.color.value)
