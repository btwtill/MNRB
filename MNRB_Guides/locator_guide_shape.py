from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

class LocatorGuideShape():
    def __init__(self, guide) -> None:
        self.guide = guide

    def draw(self):
        guide_shape = MC.createSpaceLocator(self.guide.position, self.guide.name, self.guide.color)
        self.guide.name = guide_shape

    def resize(self, size):
        MC.setLocatorLocalScale(self.guide.name, size)

    def updateColor(self):
        pass
