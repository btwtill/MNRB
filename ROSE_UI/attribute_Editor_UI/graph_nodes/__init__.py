from os.path import dirname, basename, isfile, join

import glob

#same auto-discovery the pipeline steps use: dropping a new node file in this
#folder registers it, with no central list to keep in step
modules = glob.glob(join(dirname(__file__), "*.py"))

__all__ = [basename(file)[:-3] for file in modules if isfile(file) and not file.endswith('__init__.py')]
