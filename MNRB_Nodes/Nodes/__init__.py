from os.path import dirname, basename, isfile, join

import glob

#get every file with .py ending from this files directory
modules = glob.glob(join(dirname(__file__), "*.py"))

#store all moduels that are not __init__.py in the __all__ variable
__all__ = [basename(file)[:-3] for file in modules if isfile(file) and not file.endswith('__init__.py')]