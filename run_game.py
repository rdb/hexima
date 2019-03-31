#! /usr/bin/env python

import sys

if sys.version_info < (3, 5):
    print("""
===================================================

Sorry, but this game requires Python 3.

It was tested on 3.7, but 3.5 or 3.6 may also work.

===================================================
""")
    sys.exit(1)

try:
    import panda3d
    import esper
except ImportError as ex:
    print("""
===================================================

This game requires Panda3D 1.10.2.

Please run the following command to install it:

    pip install -r requirements.txt

===================================================
""")
    print(repr(ex))
    sys.exit(1)


print("Using Panda3D {0}".format(panda3d.__version__))

from game import main
main()
