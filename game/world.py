from panda3d import core
import esper

from . import components
from . import processors
from .level import Level, TileType

from direct.interval.IntervalGlobal import LerpFunctionInterval, Func, Sequence, Parallel

import os
from random import random


class World(esper.World):
    def __init__(self):
        super().__init__(self)

        self.root = core.NodePath("world")

        self.level = None

        self.tiles = []
        self.next_levels = []

        # Add player
        player = self.create_entity()
        self.add_component(player, components.Spatial(parent=self.root))
        self.add_component(player, components.Die())
        self.add_component(player, components.Model("gfx/d6/d6.bam", offset=(0, 0, -0.5), scale=0.96/7.0))
        self.player = player

        # Create camera entity
        camera = self.create_entity()
        self.add_component(camera, components.Camera(base.camera, fov=90, pos=(0, -6.7, 0), look_at=(0, 0, 0)))
        self.add_component(camera, components.Spatial(parent=self.root, hpr=(-26.5651, -48.1897, 0)))#153.435, 48.1897, 0))) #
        self.add_component(camera, components.Compass(player, 'xy'))

        self.player_control = processors.PlayerControl(player, camera)
        self.add_processor(self.player_control)

        # Add light source
        sun = self.create_entity()
        self.add_component(sun, components.Sun((0.7, 0.4, -0.7), color_temperature=6000, intensity=9))

        self.level_root = self.root.attach_new_node("level")
        self.old_level_root = self.root.attach_new_node("old_levels")

        self.exit_tile = self.place_tile(0, 0, TileType.exit)

        self.add_processor(processors.Gravity(1.0))

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

    def win_level(self):
        if not self.next_levels:
            messenger.send('escape')
            return

        level = self.next_levels.pop(0)
        self.load_level(level)

    def load_level(self, name):
        level_dir = os.path.join(os.path.dirname(__file__), '..', 'levels')
        level = Level()
        level.read(os.path.join(level_dir, name + '.lvl'))
        self.level = level

        self.level_root.wrt_reparent_to(self.old_level_root)
        level_root = self.root.attach_new_node("level")
        self.level_root = level_root

        # Make previous tiles fall away
        #for tile in self.tiles:
        #    self.add_component(tile, components.Falling(drag=random() + 0.5))

        self.tiles.clear()

        i = 0
        entrance = None
        exit_tile = None

        for x, y, type in level.get_tiles():
            if type == TileType.entrance:
                entrance = (x, y)
                continue

            tile = self.place_tile(x, y, type)
            if type == TileType.exit:
                exit_tile = tile

            self.tiles.append(tile)

        # Reposition player and the exit tile they rode in on
        spatial = self.component_for_entity(self.player, components.Spatial)
        self.old_level_root.set_x(self.old_level_root.get_x() + entrance[0] - spatial.x)
        self.old_level_root.set_y(self.old_level_root.get_y() + entrance[1] - spatial.y)
        spatial.x = entrance[0]
        spatial.y = entrance[1]
        level_root.set_z(7)

        exit_tile_path = self.component_for_entity(self.exit_tile, components.Spatial).path
        exit_tile_path.wrt_reparent_to(level_root)

        self.exit_tile = exit_tile

        level_root.set_z(0)
        self.setup()
        level_root.set_z(7)

        Sequence(
            Parallel(
               self.old_level_root.posInterval(2.0, (self.old_level_root.get_x(), self.old_level_root.get_y(), self.old_level_root.get_z() - 10), blendType='easeOut'),
               exit_tile_path.posInterval(2.0, (exit_tile_path.get_x(), exit_tile_path.get_y(), exit_tile_path.get_z() + 7), blendType='easeOut'),
               level_root.posInterval(2.0, (level_root.get_x(), level_root.get_y(), 0), blendType='easeOut'),
            ),
            Func(self.player_control.unlock),
        ).start()

    def place_tile(self, x, y, type):
        tile = self.create_entity()

        spatial = components.Spatial("tile", parent=self.level_root, pos=(x, y))
        self.add_component(tile, spatial)
        self.add_component(tile, components.Model("gfx/tile.bam", offset=(0, 0, -0.5), scale=0.98))

        spatial.path.set_color_scale(type.get_color())

        symbol = type.get_symbol()
        if symbol:
            self.add_component(tile, components.Symbol(symbol, color=(0.5, 0, 0, 1), font=base.symbol_font))

        #glow = loader.load_model("gfx/glow.bam")
        #glow.set_attrib(core.ColorBlendAttrib.make(core.ColorBlendAttrib.M_add, core.ColorBlendAttrib.O_color_scale, core.ColorBlendAttrib.O_one))
        #glow.set_shader_off(10)
        #glow.set_depth_write(False)
        #glow.set_color_scale((0.15, 0.1, 0.1, 0.5), 100)
        #glow.set_light_off(10)
        #glow.set_material_off(10)
        #glow.set_bin('fixed', 0)
        #glow.set_pos(5, 1, -0.5)
        #glow.reparent_to(render)

        return tile
