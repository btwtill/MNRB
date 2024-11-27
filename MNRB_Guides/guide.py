from MNRB.MNRB_cmds_wrapper.cmds_wrapper import MC #type: ignore

class guide():
    def __init__(self, name, color = (1, 1, 0), position = (0, 0, 0), size = 1) -> None:
       
        self.name = name
        self.color = color

        self.position = position
        self.size = 1

    def draw(self):
        guide_shape = MC.createSpaceLocator(self.position, self.name, self.color)
        self.name = guide_shape

    def resize(self, size):
        #MC.setLocatorScale((size, size, size))
        pass