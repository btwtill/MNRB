
from MNRB.ROSE_Debug.rose_log import ROSE_Log #type: ignore
log = ROSE_Log.get("rose.editor.shelf")

def open():
    """This function is to open the the tools UI"""
    from PySide6.QtWidgets import QApplication #type: ignore
    from MNRB.ROSE_UI import rose_editor #type: ignore

    def get_active_editor_window():
        #was previously isinstance(widget, QMainWindow), which matches ANY visible
        #top-level QMainWindow in the whole Qt application, not specifically ROSE's
        #own editor - too loose to reliably prevent duplicate editor windows.
        #
        #also can't use isinstance(widget, rose_editor.rose_Editor) here - every
        #shelf Reload does importlib.reload(rose_editor), which rebuilds rose_Editor
        #as a NEW class object under the same name. A window opened before that
        #reload is an instance of the OLD class object, so isinstance against the
        #post-reload class silently returns False and the dedup check misses it -
        #comparing by name/module string survives the reload since that identity
        #doesn't change even when the class object does
        for widget in QApplication.topLevelWidgets():
            widget_class = type(widget)
            if (widget_class.__name__ == "rose_Editor"
                    and widget_class.__module__ == rose_editor.rose_Editor.__module__
                    and widget.isVisible()):
                return widget
        return None

    existing_editor = get_active_editor_window()
    if existing_editor is not None:
        existing_editor.raise_()
        existing_editor.activateWindow()
        return

    newEditor = rose_editor.rose_Editor()
    newEditor.show()

#the shelf is what performs the reload - rose_shelf_utility reloads this very
#module at its own import time - and docs/ is sphinx config rather than tool code
SKIPPED_SUBPACKAGES = ("ROSE_shelf", "docs")

def getROSEPackageName():
    return __name__.split(".")[0]

def isReloadableModule(module_name):
    package_name = getROSEPackageName()

    if module_name != package_name and not module_name.startswith(package_name + "."):
        return False

    skipped = tuple("%s.%s" % (package_name, name) for name in SKIPPED_SUBPACKAGES)
    return not module_name.startswith(skipped)

def findROSEModules(package_name, search_paths):
    """Every importable module under the package, found on disk.

    Deliberately not pkgutil.walk_packages: ROSE's subdirectories carry no
    __init__.py, so they are namespace packages, and pkgutil does not descend
    into those - it reports only ROSE_shelf (which does have one) and the
    top-level .py files, 5 modules out of 111.
    """
    import os

    module_names = set()

    for search_path in search_paths:
        for root, directory_names, file_names in os.walk(search_path):
            directory_names[:] = [name for name in directory_names
                                  if name != "__pycache__" and name.isidentifier()]

            relative_root = os.path.relpath(root, search_path)
            parent_parts = [] if relative_root == "." else relative_root.split(os.sep)

            for file_name in file_names:
                if not file_name.endswith(".py"):
                    continue

                stem = file_name[:-3]
                name_parts = parent_parts if stem == "__init__" else parent_parts + [stem]

                if not name_parts or not all(part.isidentifier() for part in name_parts):
                    continue

                module_names.add(".".join([package_name] + name_parts))

    return sorted(module_names)

def sortRegistryModulesFirst(module_names):
    """The one ordering constraint the import machinery cannot work out on its own.

    Each editor's conf module ends with `from <its package> import *` to populate
    its registry, while the modules it reaches import back through the node base
    to read that same conf. That cycle is only safe entered from the conf: the
    conf defines its API before the star-import line, so an inner module reading
    it mid-flight still finds what it needs.

    Entered from the other side it breaks badly and quietly - importing a node
    module first sends the cycle through the conf, whose star-import then finds
    that node module half-initialised and raises. The siblings the failed cascade
    already imported stay bound to a conf that is then discarded, so when the conf
    is imported cleanly later their registrations never re-run and the registry
    comes back with a fraction of its node types rather than an error.
    """
    def isRegistryModule(module_name):
        return module_name.rpartition(".")[2].endswith("conf")

    return sorted(module_names, key = lambda name: (not isRegistryModule(name), name))

def reloadROSEModules():
    """Reload every ROSE module, in whatever order their own imports require.

    This was a hand-maintained list of ~100 importlib.reload calls in a
    hand-maintained order, which failed two ways. A module nobody remembered to
    add never reloaded at all - skinning_Editor_Scene never did, so editing it
    and hitting Reload did nothing. And a module listed *before* something it
    imports kept that dependency's old classes, which is how a reloaded Enum
    ended up with members that compared unequal to their own class and raised
    KeyError on the first build after a Reload.

    Dropping the package out of sys.modules and importing it again removes both:
    there is no list to fall out of date, and the import machinery works out the
    order itself, since importing a module imports what it needs first.

    One constraint it cannot work out is the conf/registry cycle - see
    sortRegistryModulesFirst, which is the only ordering this still imposes.
    """
    import importlib, sys

    package_name = getROSEPackageName()
    log.debug("Reloading ROSE Shelf and Modules............")

    #kept so a failure to re-import the package leaves the session on the last
    #working code rather than on no code at all
    saved_modules = {name: module for name, module in sys.modules.items()
                     if isReloadableModule(name)}
    for name in saved_modules:
        del sys.modules[name]

    try:
        package = importlib.import_module(package_name)
        #a namespace package can list the same directory more than once, once per
        #matching sys.path entry
        search_paths = list(dict.fromkeys(package.__path__))
        module_names = findROSEModules(package_name, search_paths)
    except Exception:
        sys.modules.update(saved_modules)
        raise

    reloaded_count = 0
    failed_modules = []

    for module_name in sortRegistryModulesFirst(module_names):
        if not isReloadableModule(module_name):
            continue

        if module_name in sys.modules:
            #already pulled in by something imported earlier this pass, so it is
            #just as fresh - everything was dropped from sys.modules above.
            #Asking for it again by name would trip the parent-attribute check on
            #packages whose __init__ imports their own children: node_Editor_conf
            #ends with `from MNRB.ROSE_Nodes.Nodes import *`, and each node module
            #imports back through rose_node_base, so the cycle leaves the parent
            #package's attribute unbound even though the module itself is loaded
            reloaded_count += 1
            continue

        try:
            importlib.import_module(module_name)
            reloaded_count += 1
        except Exception as error:
            #not rolled back: a module that failed to import is simply absent, so
            #the next import of it raises again where it is actually used, rather
            #than silently running last session's code
            failed_modules.append((module_name, error))

    if failed_modules:
        log.warning("ROSE reload: %d module(s) failed to import:" % len(failed_modules))
        for module_name, error in failed_modules:
            log.warning("   %s -> %s: %s" % (module_name, type(error).__name__, error))

    log.debug("Reloaded", reloaded_count, "ROSE modules")
    return reloaded_count, failed_modules
