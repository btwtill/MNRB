
class MNRB_Side():
    def __init__(self, side_name, side_prefix) -> None:
        self.side = side_name
        self.prefix = side_prefix

class MNRB_Names():
    left = MNRB_Side("left", "L_")
    right = MNRB_Side("right", "R_")
    middle = MNRB_Side("middle", "M_")