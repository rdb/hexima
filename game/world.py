from panda3d import core
import esper

from . import components
from . import processors
from .level import Level

import os
from random import random

DEFAULT_LVL = "level8"


class World(esper.World):
    def __init__(self):
        super().__init__(self)

        self.symbol_font = loader.load_font("font/DejaVuSans.ttf")
        self.symbol_font.set_pixels_per_unit(64)

        self.root = core.NodePath("world")

        self.level = None
        self.load_level(DEFAULT_LVL)

        self.tiles = []

        # Add player
        player = self.create_entity()
        self.add_component(player, components.Spatial(parent=self.root, pos=self.level.entrance))
        self.add_component(player, components.Die())
        self.add_component(player, components.Model("gfx/d6/d6.bam", offset=(0, 0, -0.5), scale=0.96/7.0))

        self.add_processor(processors.PlayerControl(player))

        # Create camera entity
        camera = self.create_entity()
        self.add_component(camera, components.Camera(base.camera, fov=90, pos=(-2, -4, 5), look_at=(0, 0, 0)))
        self.add_component(camera, components.Spatial(parent=self.root))
        self.add_component(camera, components.Compass(player, 'xy'))

        # Add light source
        sun = self.create_entity()
        self.add_component(sun, components.Sun((0.7, 0.7, -1), color_temperature=6000, intensity=10))

        self.setup()

    def setup(self):
        "One-time scene graph set-up after components are added/removed."

        # Set up models
        for ent, model in self.get_component(components.Model):
            model.setup(self, ent)

        # Set up compass effects
        for ent, compass in self.get_component(components.Compass):
            compass.setup(self, ent)

        # Set up cameras
        for ent, camera in self.get_component(components.Camera):
            camera.setup(self, ent)

        # Set up lights
        for ent, sun in self.get_component(components.Sun):
            sun.setup(self, ent)

        # You get the point by now
        for ent, symbol in self.get_component(components.Symbol):
            symbol.setup(self, ent)

    def load_level(self, name):
        level_dir = os.path.join(os.path.dirname(__file__), '..', 'levels')
        level = Level()
        level.read(os.path.join(level_dir, name + '.lvl'))
        self.level = level

        for x, y, type in level.get_tiles():
            tile = self.create_entity()

            self.add_component(tile, components.Spatial("tile", parent=self.root, pos=(x, y)))
            self.add_component(tile, components.Model("gfx/tile.bam", offset=(0, 0, -0.5), scale=0.98))

            symbol = type.get_symbol()
            if symbol:
                self.add_component(tile, components.Symbol(symbol, color=(0.5, 0, 0, 1), font=self.symbol_font))
            #self.add_component(tile, components.Model(type + ".bam",
            #    offset=(0, 0, -0.5 - 1.0 / 7.0 - random() * 0.01),
            #    scale=(0.96 / 7, 0.96 / 7, 0.96 / 7)))
