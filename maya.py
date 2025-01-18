import sys
import os
from importlib import reload

home_dir = os.getenv("HOME")
<<<<<<< HEAD
print("home dir:", home_dir)
=======
print("home_dir:", home_dir)
>>>>>>> ff0723d (fix path join bug)
if(not home_dir):
    raise Exception("could not open home directory")

package_path = os.path.join(home_dir, "MSc-CAVE/Units/CGI_Tools/Maya-Ball/")
<<<<<<< HEAD
print("package_path", package_path)
if(not os.path.exists(package_path)):
    raise Exception("could not find package path")
sys.path.append(package_path)
=======
sys.path.append(package_path)
print("package path:", package_path)
>>>>>>> ff0723d (fix path join bug)

import package.main

reload(package.main)
from package.main import main

main()
