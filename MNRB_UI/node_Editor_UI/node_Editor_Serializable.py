
CLASS_DEBUG = False

class Serializable():
    def __init__(self) -> None:
        self.id = id(self)
        if CLASS_DEBUG : print("SERIALIZABLE:: -__init__:: Initialized a Serializable Class")