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
        self.disable_mouse()

        self.set_background_color((0.31, 0.42, 0.53))

        self.world = World()
        self.world.root.reparent_to(self.render)

        self.task_mgr.add(self.process_world)

    def __del__(self):
        core.unload_prc_file(self.settings)

    def process_world(self, task):
        self.world.process(globalClock.dt)
        return task.cont
