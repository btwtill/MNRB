"""Loading rig-specific node packs.

A pack is a folder holding a `rose_pack.json` manifest and the Python modules for
the node types it provides. Packs live with the rig they belong to, not in this
repo, so a component written for one rig never lands in the core registry
pretending to be general-purpose.

The persistence split is deliberate:
  - *where packs live* is per machine, and sits in QSettings next to the other
    application preferences
  - *what a pack contains* - its categories and its nodes - is in the manifest,
    so it travels with the rig and anyone cloning that repo gets the same nodes
    without configuring anything
"""

import importlib.util
import json
import os
import sys

from PySide6.QtCore import QSettings #type: ignore

from MNRB.ROSE_Nodes.node_Editor_conf import (ROSE_NODES, ROSE_NODE_CATEGORIES, #type: ignore
                                              registerNodeCategory)
from MNRB.ROSE_cmds_wrapper.cmds_wrapper import MC #type: ignore
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore

log = ROSE_Log.get("rose.packs")

MANIFEST_NAME = "rose_pack.json"
SETTINGS_KEY = "node_pack_paths"

#pack modules are imported under this prefix so they cannot collide with MNRB's
#own modules or with each other
MODULE_PREFIX = "rose_pack"

#pack_id -> {"path": ..., "label": ..., "type_ids": [...], "requires_plugins": [...]}
LOADED_PACKS = {}
#pack folders that were configured but could not be loaded, for the UI to show
FAILED_PACKS = {}

# Where packs live (per machine)

def getPackSearchPaths():
    stored = QSettings("tlpf", "ROSE").value(SETTINGS_KEY, [])

    #QSettings hands a single-entry list back as a bare string
    if isinstance(stored, str):
        stored = [stored] if stored else []

    return [path for path in (stored or []) if path]

def setPackSearchPaths(paths):
    QSettings("tlpf", "ROSE").setValue(SETTINGS_KEY, list(dict.fromkeys(paths)))

def addPackSearchPath(path):
    paths = getPackSearchPaths()
    if path not in paths:
        paths.append(path)
        setPackSearchPaths(paths)
    return paths

def removePackSearchPath(path):
    paths = [existing for existing in getPackSearchPaths() if existing != path]
    setPackSearchPaths(paths)
    return paths

# Reading a manifest

def readManifest(pack_path):
    manifest_path = os.path.join(pack_path, MANIFEST_NAME)

    if not os.path.isfile(manifest_path):
        raise FileNotFoundError("no %s in '%s'" % (MANIFEST_NAME, pack_path))

    with open(manifest_path, "r") as manifest_file:
        manifest = json.load(manifest_file)

    pack_id = manifest.get("pack_id")
    if not pack_id:
        raise ValueError("'%s' has no pack_id" % manifest_path)

    for node in manifest.get("nodes", []):
        type_id = node.get("type_id", "")
        #the prefix is what makes ids collision-free, so a pack that does not use
        #its own is rejected rather than quietly allowed to squat on another's
        if not type_id.startswith(pack_id + "."):
            raise ValueError("node type '%s' in pack '%s' must start with '%s.'"
                             % (type_id, pack_id, pack_id))

    return manifest

# Registering and unregistering

def unregisterPack(pack_id):
    """Drop a pack's nodes and categories so loading it again is idempotent."""
    for type_id in [key for key in ROSE_NODES if str(key).startswith(pack_id + ".")]:
        del ROSE_NODES[type_id]

    for category_id in [key for key in ROSE_NODE_CATEGORIES if str(key).startswith(pack_id + ".")]:
        del ROSE_NODE_CATEGORIES[category_id]

    for module_name in [name for name in sys.modules
                        if name.startswith("%s.%s." % (MODULE_PREFIX, pack_id))]:
        del sys.modules[module_name]

    LOADED_PACKS.pop(pack_id, None)

def importPackModule(pack_id, pack_path, module_name):
    qualified_name = "%s.%s.%s" % (MODULE_PREFIX, pack_id, module_name)
    module_path = os.path.join(pack_path, module_name + ".py")

    if not os.path.isfile(module_path):
        raise FileNotFoundError("pack '%s' declares module '%s', which is not in %s"
                                % (pack_id, module_name, pack_path))

    spec = importlib.util.spec_from_file_location(qualified_name, module_path)
    module = importlib.util.module_from_spec(spec)
    #registered before execution so a module importing itself indirectly resolves
    sys.modules[qualified_name] = module
    spec.loader.exec_module(module)
    return module

def loadPack(pack_path):
    manifest = readManifest(pack_path)
    pack_id = manifest["pack_id"]

    unregisterPack(pack_id)

    for category in manifest.get("categories", []):
        registerNodeCategory(category["id"], category.get("label", category["id"]),
                             category.get("order", 100))

    declared_type_ids = []
    for node in manifest.get("nodes", []):
        #the module registers its own class with @registerNode, exactly as a core
        #component does - the manifest says what to import and what to expect
        importPackModule(pack_id, pack_path, node["module"])
        declared_type_ids.append(node["type_id"])

    missing = [type_id for type_id in declared_type_ids if type_id not in ROSE_NODES]
    if missing:
        raise ValueError("pack '%s' declares %s but importing its modules registered nothing for them"
                         % (pack_id, missing))

    LOADED_PACKS[pack_id] = {
        "path": pack_path,
        "label": manifest.get("label", pack_id),
        "type_ids": declared_type_ids,
        "requires_plugins": manifest.get("requires_plugins", []),
    }
    FAILED_PACKS.pop(pack_path, None)

    log.debug("PACKS:: --loadPack:: loaded '%s' with %d node type(s)" % (pack_id, len(declared_type_ids)))
    return LOADED_PACKS[pack_id]

def loadAllPacks():
    """Load every configured pack. Returns (loaded, failed)."""
    FAILED_PACKS.clear()

    for pack_path in getPackSearchPaths():
        try:
            loadPack(pack_path)
        except Exception as error:
            #one broken pack must not stop the others, or the editor
            FAILED_PACKS[pack_path] = error
            log.warning("PACKS:: could not load pack at '%s': %s: %s"
                        % (pack_path, type(error).__name__, error))

    return dict(LOADED_PACKS), dict(FAILED_PACKS)

def getPackNodeEntries(pack_path):
    """The node entries a pack's manifest declares, as written."""
    try:
        return readManifest(pack_path).get("nodes", [])
    except Exception:
        return []

def removeNodeTypeFromPack(pack_path, type_id, delete_module_file = False):
    """Drop one node type from a pack.

    Removes it from the manifest and unregisters it, so it stops appearing in the
    palette. The module file is left alone unless explicitly asked for - it is the
    user's own code, and an orphan module is harmless because the loader only
    imports what the manifest lists.

    Returns the module path, so a caller can say where the file was left.
    """
    manifest_path = os.path.join(pack_path, MANIFEST_NAME)

    with open(manifest_path, "r") as manifest_file:
        manifest = json.load(manifest_file)

    remaining = []
    removed_entry = None
    for entry in manifest.get("nodes", []):
        if entry.get("type_id") == type_id:
            removed_entry = entry
        else:
            remaining.append(entry)

    if removed_entry is None:
        raise ValueError("'%s' is not declared in %s" % (type_id, manifest_path))

    manifest["nodes"] = remaining
    with open(manifest_path, "w") as manifest_file:
        json.dump(manifest, manifest_file, indent=4)

    module_path = os.path.join(pack_path, removed_entry.get("module", "") + ".py")

    if delete_module_file and os.path.isfile(module_path):
        os.remove(module_path)

    #reloading drops the whole pack and re-registers what the manifest still lists,
    #which is what actually takes the type out of ROSE_NODES
    loadPack(pack_path)

    log.debug("PACKS:: --removeNodeTypeFromPack:: removed '%s' from '%s'" % (type_id, pack_path))
    return module_path

# What a graph depends on

def getPackForTypeId(type_id):
    prefix = str(type_id).split(".")[0]
    return LOADED_PACKS.get(prefix)

def describeAuthoringRequirements(type_ids):
    """What is needed to OPEN and BUILD a graph made of these node types.

    Node packs are an authoring dependency only: they supply the component
    classes that build the rig, and nothing of them survives into the published
    file. An animator opening the built rig needs none of this - see
    describeRuntimePlugins for what they do need.
    """
    required_packs = {}
    missing_packs = set()

    for type_id in type_ids:
        prefix = str(type_id).split(".")[0]
        if prefix == "rose":
            continue
        if prefix in LOADED_PACKS:
            required_packs[prefix] = LOADED_PACKS[prefix]
        else:
            missing_packs.add(prefix)

    #what the packs say they may create. A declaration, so it is the right answer
    #for "can this machine build the rig" and the wrong one for "what does the
    #published rig need" - a component can declare a plugin and not use it here.
    build_plugins = sorted({plugin for pack in required_packs.values()
                            for plugin in pack.get("requires_plugins", [])})

    return {"packs": required_packs,
            "missing_packs": sorted(missing_packs),
            "build_plugins": build_plugins,
            "missing_build_plugins": [plugin for plugin in build_plugins
                                      if not MC.isPluginLoaded(plugin)]}

def describeRuntimePlugins(nodes):
    """What an animator needs installed to open the BUILT rig.

    Inspected from the nodes that are actually in the hierarchy being published,
    not declared, because only what was really created matters to whoever opens
    the file. Maya records these as `requires` lines itself, which makes the rig
    fail loudly without them - this is so the publish can ship them instead.
    """
    return MC.getRequiredPluginsForNodes(nodes)
