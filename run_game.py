#! /usr/bin/env python

import sys

try:
    import panda3d
    import esper
except ImportError as ex:
    print("""
===================================================

This game requires Panda3D 1.10.2 and esper.

Please run the following command to install them:

    pip install -r requirements.txt

===================================================
""")
    print(repr(ex))
    sys.exit(1)


print("Using Panda3D {0}".format(panda3d.__version__))

from game import main
main()
