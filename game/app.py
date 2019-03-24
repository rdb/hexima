import sys

from direct.showbase.ShowBase import ShowBase
from panda3d import core
import pman.shim

from .world import World


class GameApp(ShowBase):
    def __init__(self):
        self.settings = core.load_prc_file(core.Filename.expand_from("$MAIN_DIR/settings.prc"))

        ShowBase.__init__(self)
        pman.shim.init(self)
        self.accept('escape', sys.exit)

        self.world = World()

    def __del__(self):
        core.unload_prc_file(self.settings)
