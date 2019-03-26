from panda3d import core
import esper

from . import components
from . import processors
from .level import Level

import os


class World(esper.World):
    def __init__(self):
        super().__init__(self)

        self.root = core.NodePath("world")

        # Create camera entity
        camera = self.create_entity()
        self.add_component(camera, components.Camera(base.camera, fov=90, pos=(-1, -1, 20), look_at=(5, 5, 0)))

        self.level = None
        self.load_level("level0")

        self.tiles = []

        self.add_processor(processors.Movement())

        # Add player
        player = self.create_entity()
        self.add_component(player, components.Spatial(parent=self.root, pos=self.level.entrance))
        self.add_component(player, components.Die())
        self.add_component(player, components.Model("gfx/d6/d6.bam", offset=(0, 0, -0.5), scale=1.0/7.0))

        self.add_processor(processors.PlayerControl(player))

    def load_level(self, name):
        level_dir = os.path.join(os.path.dirname(__file__), '..', 'levels')
        level = Level()
        level.read(os.path.join(level_dir, name + '.lvl'))
        self.level = level

        for x, y, type in level.get_tiles():
            tile = self.create_entity()

            self.add_component(tile, components.Spatial("tile", parent=self.root, pos=(x, y)))
            self.add_component(tile, components.Model(type + ".bam",
                offset=(0, 0, -0.5 - 1.0 / 7.0),
                scale=(1.0 / 7, 1.0 / 7, 1.0 / 7)))
