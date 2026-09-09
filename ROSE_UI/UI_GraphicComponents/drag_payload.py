from PySide6.QtCore import QByteArray, QDataStream, QIODevice #type: ignore

"""Shared drag payload for ROSE's list-to-list drags.

Every one of them carries the same thing - an ordered list of (id, name) pairs
for whatever is being dragged - so the deform, attribute and control lists all
use this rather than each rolling its own QDataStream layout. Only the mimetype
differs, which is what keeps a deform from being droppable on a control box.
"""

def encodeIdNamePayload(entries):
    """entries: a list of (id, name). Count-prefixed, so one drag carries a whole
    multi selection or a whole group as easily as a single row."""
    payload = QByteArray()
    data_stream = QDataStream(payload, QIODevice.WriteOnly)

    data_stream.writeInt32(len(entries))
    for entry_id, entry_name in entries:
        data_stream.writeInt64(entry_id)
        data_stream.writeQString(entry_name)

    return payload

def decodeIdNamePayload(payload):
    data_stream = QDataStream(payload, QIODevice.ReadOnly)

    entries = []
    for _ in range(data_stream.readInt32()):
        entry_id = data_stream.readInt64()
        entry_name = data_stream.readQString()
        entries.append((entry_id, entry_name))

    return entries
