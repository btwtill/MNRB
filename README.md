# ROSE Editor

* Tested Supported Maya Versions: __2023__
* Pyhthon Version: 

## Installation

### Prerequisites

* Maya is installed
* You figured out where your scrips directory is
  * Windows: /Home/Users/__yourUserName__/Documents/maya/scripts
  * Mac: /Users/__yourUserName__/Library/Preferences/Autodesk/maya/scripts
    * beware that by default this directory is not accessable with the finder since it is a hidden folder

### First install

Copy this repository into your scritps directory.

To get the tool up and running the first thing is to open maya. Then find the Script Editor. Located under the __Windows__ --> __General Editors__ --> __Script Editor__. 
There access a new python tab and enter the following code

```
Python: 

from MNRB.ROSE_shelf import rose_shelf_utility
import importlib
importlib.reload(rose_shelf_utility)
rose_shelf_utility.loadROSEShelf(name="rose_shelf")

```

If this code runs succesfully you will have a new shelf in your shelf bar with access to the __ROSE__ Editor.

### userSetup.py

If you want the shelf to load on startup of maya you have to either create a `userSetup.py` file in the `/scripts` directory and add the following content. Or if you already have the file simply add the next lines to the file.

```
import maya.utils


# ==========================================
# Load ROSE Shelf
# ==========================================

from MNRB.ROSE_shelf import rose_shelf_utility

def load_user_shelf():
    rose_shelf_utility.loadROSEShelf(name="rose_shelf")

maya.utils.executeDeferred("load_user_shelf()")
```

## Documentation

*  Code and API Documentation can be found in the [docs build](./docs/build/html/) directory
* User/Feature documentation is still in the works

## More Information