import uuid

CLASS_DEBUG = False

#63 bit so an id still fits a signed 64-bit int - they go through
#QDataStream.writeInt64() in the skinning tab's drag payload
ID_BIT_WIDTH = 63

def generateSerializableId() -> int:
    #not id(self): CPython reuses a collected object's address, so a rebuild -
    #which drops and recreates every deform at once - could hand a new object a
    #dead one's id, and the skinning tab tracks deforms by id across rebuilds.
    #Random rather than a counter, which importlib.reload() would reset to the
    #start while objects holding the low ids are still alive.
    return uuid.uuid4().int >> (128 - ID_BIT_WIDTH)

class Serializable():
    def __init__(self) -> None:
        self.id = generateSerializableId()
        if CLASS_DEBUG : print("SERIALIZABLE:: -__init__:: Initialized a Serializable Class")

    def serialize(self):
        raise NotImplemented

    def deserialize(self, data, hashmap={}, restore_id = True):
        raise NotImplemented
