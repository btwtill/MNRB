"""The set of log channels ROSE writes to.

One flat list, with the tree implied by the dotted names - the preferences UI
builds its tree from these, and ROSE_Log resolves "is this on?" by walking the
same dots upward, so enabling a parent enables everything under it.

Adding a channel here is all that is needed for it to appear in preferences.
"""

#(channel name, label shown in the preferences tree)
ROSE_LOG_CHANNELS = [
    ("rose",                                "ROSE"),

    ("rose.editor",                         "Editor Shell"),
    ("rose.editor.project",                 "Project Open / Save"),
    ("rose.editor.shelf",                   "Shelf / Module Loading"),

    ("rose.node_editor",                    "Node Editor"),
    ("rose.node_editor.scene",              "Scene"),
    ("rose.node_editor.node",               "Nodes"),
    ("rose.node_editor.socket",             "Sockets"),
    ("rose.node_editor.edge",               "Edges"),
    ("rose.node_editor.view",               "View / Input Events"),
    ("rose.node_editor.selection",          "Selection"),
    ("rose.node_editor.history",            "Undo / Redo / Clipboard"),
    ("rose.node_editor.properties",         "Property Panels"),
    ("rose.node_editor.dragdrop",           "Drag & Drop"),

    ("rose.skinning",                       "Skinning Editor"),
    ("rose.skinning.deform_list",           "Deform List"),
    ("rose.skinning.cluster",               "Skin Clusters"),
    ("rose.skinning.dragdrop",              "Drag & Drop"),

    ("rose.pipeline",                       "Build Pipeline"),
    ("rose.pipeline.steps",                 "Steps"),

    ("rose.components",                     "Components"),
    ("rose.components.guides",              "Guides"),
    ("rose.components.deforms",             "Deforms"),
    ("rose.components.controls",            "Controls"),
    ("rose.components.validation",          "Validation"),

    ("rose.scene",                          "Rig Hierarchy"),
    ("rose.serialize",                      "Save / Load"),
    ("rose.maya",                           "Maya Command Wrapper"),
]

def getChannelNames():
    return [channel for channel, _label in ROSE_LOG_CHANNELS]

def getChannelLabel(channel):
    for name, label in ROSE_LOG_CHANNELS:
        if name == channel:
            return label
    return channel
