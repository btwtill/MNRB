"""Packaging a rig's external files - textures, image sequences - with its export.

A shipped rig has to carry everything it points at: an animator opening it
somewhere else must not find empty texture paths. At export the Output Path
step:

  1. COLLECTS every external file the rig uses. Two sources:
     - the file textures Maya would export with the rig: anything upstream of
       the rig hierarchy, and the shading of its geometry (findSceneAssets)
     - files a component declares itself (ROSE_Node.getExternalAssets), for
       paths no shading network reveals - the screen face's image layers are
       written as attributes for the render scene, for instance
  2. COPIES them into a folder next to the exported file - a sequence with all
     its frames, same-named files from different folders kept apart, files that
     have not changed since the last export skipped
  3. REPOINTS every path at its copy for the export, and puts the working scene
     back right after, so the workfile keeps the paths it had

The exported paths are absolute, to the copies. Relative ones are not reliable -
Maya turns a texture path absolute when it saves - and the screen face's paths
travel through Alembic to a render scene, where a relative path would resolve
against the wrong project. A moved package is one folder to repoint in Maya's
File Path Editor.
"""

import glob
import os
import re
import shutil

import maya.cmds as cmds #type: ignore

from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore
log = ROSE_Log.get("rose.pipeline.steps")

DEFAULT_ASSET_FOLDER = "textures"

#node type -> the attribute holding its file path. Only Maya's file texture for
#now; another texture node that reads a file is one entry here
FILE_PATH_ATTRIBUTES = {
    "file": "fileTextureName",
}

#name.0001.ext - the frame number, and what is either side of it
FRAME_PATTERN = re.compile(r"^(?P<head>.*?)(?P<frame>\d+)(?P<tail>\.[^.\\/]+)$")


class RigAsset:
    """One external file (or sequence) the rig uses, and how to repoint it.

    `assign(path)` writes a path wherever the rig keeps this file's path. It is
    called with the packaged copy's path for the export, and with the original
    again afterwards."""

    def __init__(self, path, assign, sequence = False, label = ""):
        self.path = path
        self.assign = assign
        self.sequence = sequence
        self.label = label or os.path.basename(path)


def findSceneAssets(root_nodes):
    """RigAssets for the file textures exported with these nodes: their history,
    and the shading of every mesh under them."""
    if not root_nodes:
        return []
    dag = cmds.listRelatives(root_nodes, allDescendents = True, fullPath = True) or []
    dag += cmds.ls(root_nodes, long = True) or []

    related = set(cmds.listHistory(dag, pruneDagObjects = False) or [])
    shapes = cmds.ls(dag, type = ("mesh", "nurbsSurface", "nurbsCurve"), long = True) or []
    engines = set(cmds.listConnections(shapes, type = "shadingEngine") or []) if shapes else set()
    if engines:
        related.update(cmds.listHistory(list(engines)) or [])

    assets = []
    for node in cmds.ls(list(related), type = list(FILE_PATH_ATTRIBUTES)) or []:
        attribute = FILE_PATH_ATTRIBUTES[cmds.nodeType(node)]
        path = cmds.getAttr("%s.%s" % (node, attribute)) or ""
        if not path:
            continue
        sequence = cmds.nodeType(node) == "file" and bool(cmds.getAttr(node + ".useFrameExtension"))
        assets.append(RigAsset(path, makeAttributeAssigner(node, attribute), sequence, label = node))
    return assets


def makeAttributeAssigner(node, attribute):
    def assign(path):
        if cmds.objExists(node):
            cmds.setAttr("%s.%s" % (node, attribute), path, type = "string")
    return assign


def resolvePath(path):
    return os.path.normpath(os.path.expanduser(os.path.expandvars(path)))


def findSequenceFrames(path):
    """Every frame of the sequence `path` is one frame of, in order - same name
    either side of the frame number, any frame number."""
    directory, name = os.path.split(resolvePath(path))
    match = FRAME_PATTERN.match(name)
    if not match:
        return [resolvePath(path)] if os.path.isfile(resolvePath(path)) else []
    pattern = re.compile("^%s\\d+%s$" % (re.escape(match.group("head")), re.escape(match.group("tail"))))
    frames = [os.path.join(directory, entry) for entry in os.listdir(directory or ".") if pattern.match(entry)] \
        if os.path.isdir(directory or ".") else []
    return sorted(frames)


def isUpToDate(source, destination):
    """Copied before and not changed since - copy2 keeps the modification time."""
    if not os.path.isfile(destination):
        return False
    source_stat, destination_stat = os.stat(source), os.stat(destination)
    return (source_stat.st_size == destination_stat.st_size
            and int(destination_stat.st_mtime) >= int(source_stat.st_mtime))


class AssetPackage:
    """Copies a set of RigAssets into one folder and repoints them there - and
    back. Use as:

        package = AssetPackage(assets, folder)
        package.copy()
        package.repoint()
        try: export
        finally: package.restore()
    """

    def __init__(self, assets, folder):
        self.assets = assets
        self.folder = folder
        #source key -> packaged path, so one file used twice is copied once
        self.packaged = {}
        self.used_names = {}
        self.copied = 0
        self.skipped = 0
        self.missing = []
        self.restore_actions = []

    def copy(self):
        os.makedirs(self.folder, exist_ok = True)
        for asset in self.assets:
            key = (resolvePath(asset.path), asset.sequence)
            if key in self.packaged:
                continue
            packaged = self.copyAsset(asset)
            if packaged is not None:
                self.packaged[key] = packaged
        return self

    def copyAsset(self, asset):
        source = resolvePath(asset.path)
        if asset.sequence:
            frames = findSequenceFrames(source)
            if not frames:
                self.missing.append("%s (%s)" % (asset.path, asset.label))
                return None
            match = FRAME_PATTERN.match(os.path.basename(source))
            head, tail = match.group("head"), match.group("tail")
            new_head = self.claimName(head, tail, os.path.dirname(source), is_sequence = True)
            for frame in frames:
                frame_number = FRAME_PATTERN.match(os.path.basename(frame)).group("frame")
                self.copyFile(frame, os.path.join(self.folder, new_head + frame_number + tail))
            #the frame the rig named, in the packaged sequence
            return os.path.join(self.folder, new_head + match.group("frame") + tail)

        if not os.path.isfile(source):
            self.missing.append("%s (%s)" % (asset.path, asset.label))
            return None
        stem, extension = os.path.splitext(os.path.basename(source))
        name = self.claimName(stem, extension, os.path.dirname(source), is_sequence = False)
        destination = os.path.join(self.folder, name + extension)
        self.copyFile(source, destination)
        return destination

    def claimName(self, stem, extension, source_directory, is_sequence):
        """A name in the package for files from source_directory - the file's own
        name, unless a file of that name from another folder has it already."""
        key = (stem, extension, is_sequence)
        owner = self.used_names.get(key)
        if owner is None or owner == source_directory:
            self.used_names[key] = source_directory
            return stem
        number = 1
        while True:
            #a sequence's head ends in its separator ("blink.") - the number goes before it
            candidate = (stem.rstrip("._") + "_%d" % number + stem[len(stem.rstrip("._")):]) if is_sequence \
                else "%s_%d" % (stem, number)
            if self.used_names.get((candidate, extension, is_sequence)) in (None, source_directory):
                self.used_names[(candidate, extension, is_sequence)] = source_directory
                return candidate
            number += 1

    def copyFile(self, source, destination):
        if isUpToDate(source, destination):
            self.skipped += 1
            return
        shutil.copy2(source, destination)
        self.copied += 1

    def repoint(self):
        """Point every asset at its packaged copy, remembering how to go back."""
        for asset in self.assets:
            packaged = self.packaged.get((resolvePath(asset.path), asset.sequence))
            if packaged is None:
                continue
            asset.assign(packaged)
            self.restore_actions.append((asset.assign, asset.path))

    def restore(self):
        """Back to the paths the working scene had - last change first."""
        for assign, path in reversed(self.restore_actions):
            try:
                assign(path)
            except Exception as error:
                log.warning("AssetPackage:: --restore:: could not restore '%s': %s" % (path, error))
        self.restore_actions = []

    def summary(self):
        files = self.copied + self.skipped
        text = "%d file(s) in %s" % (files, os.path.basename(self.folder))
        if self.skipped:
            text += " (%d unchanged)" % self.skipped
        if self.missing:
            text += " - %d missing: %s" % (len(self.missing), ", ".join(self.missing))
        return text
