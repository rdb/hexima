from panda3d import core
import esper

from . import components
from . import processors
from . import ui
from .level import Level, TileType

from direct.interval.IntervalGlobal import LerpFunctionInterval, Func, Sequence, Parallel

import os
from random import random, randint


class World(esper.World):
    def __init__(self):
        super().__init__(self)

        self.root = core.NodePath("world")

        # Add fog here for now
        fog = core.Fog("fog")
        fog.color = (0.31, 0.42, 0.53, 1.0)
        fog.set_linear_range(10, 25)
        self.root.set_fog(fog)

        self.level = None

        self.tiles = {}
        self.old_tiles = []
        self.next_levels = []

        # Add player
        player = self.create_entity()
        self.add_component(player, components.Spatial(parent=self.root))
        self.add_component(player, components.Die())
        self.add_component(player, components.Model("gfx/d6/d6.bam", offset=(0, 0, -0.5), scale=0.96/7.0))
        self.player = player

        # Create camera entity
        camera = self.create_entity()
        self.add_component(camera, components.Camera(base.camera, fov=90, pos=(0, -8, 0), look_at=(0, 0, 0)))
        self.add_component(camera, components.Spatial(parent=self.root, hpr=(-26.5651, -48.1897, 0)))#153.435, 48.1897, 0))) #
        self.add_component(camera, components.Compass(player, 'xy'))

        self.player_control = processors.PlayerControl(player, camera)
        self.add_processor(self.player_control)

        # Add light source
        sun = self.create_entity()
        self.add_component(sun, components.Sun((0.7, 0.4, -0.7), color_temperature=6000, intensity=2.05))

        self.teleporters = set()
        self.toggle_tiles = set()
        self.toggle_state = False

        self.level_root = self.root.attach_new_node("level")
        self.old_level_root = self.root.attach_new_node("old_levels")

        self.tiles[(0, 0)] = self.place_tile(0, 0, TileType.exit)

        self.add_processor(processors.Gravity(1.0))

        self.hud = ui.HUD()
        ui.Button(self.hud, "      reset", (0.2, -0.13), icon="", command=self.player_control.on_reload, anchor='top-left')

        self.move_counter = ui.Indicator(self.hud, 0, (-0.17, -0.13), anchor='top-right')

        #self.die_icon = ui.Icon(self.hud, '', (0.0, -0.15), anchor='top-center')
        self.die_icon = ui.Icon(self.hud, '', (-0.15, 0.1), anchor='bottom-right')
        self.die_icon.path.set_color_scale(1, 1, 1, 1)

        self.setup()

    def delete_entity(self, ent):
        assert ent not in self.tiles.values()
        esper.World.delete_entity(self, ent)
        self._clear_dead_entities()

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

    def on_player_move(self):
        self.hud.show()

        if base.move_sound:
            base.move_sound.play()

        new_value = self.move_counter.inc_value()
        if self.level.par is not None and new_value > self.level.par:
            self.move_counter.set_icon('', style='regular')

        die = self.component_for_entity(self.player, components.Die)

        self.die_icon.set(' '[die.die.bottom_number])

    def on_level_start(self):
        self.player_control.unlock()

        spatial = self.component_for_entity(self.player, components.Spatial)
        die = self.component_for_entity(self.player, components.Die)
        spatial.path.set_hpr(0, 0, 0)
        die.die.reset()
        self.toggle_state = False

        # Delete old tiles
        while len(self.old_tiles) > 2:
            oldest_tiles = self.old_tiles.pop(0)
            for tile in oldest_tiles:
                self.delete_entity(tile)

        if self.level.par is not None:
            self.move_counter.set_icon('', style='solid')
        else:
            self.move_counter.clear_icon()
        self.move_counter.set_value(0)

    def toggle_button(self):
        self.toggle_state = not self.toggle_state

        parallel = []

        for x, y in self.toggle_tiles:
            type = self.level.get_tile(x, y)
            tile = self.tiles[(x, y)]
            spatial = self.component_for_entity(tile, components.Spatial)

            pos = core.Point3(spatial.path.get_pos())
            if type.is_passable(1, self.toggle_state):
                pos.y = y
                pos.z = 0.0
                parallel.append(spatial.path.hprInterval(0.75, (0, 0, 0), blendType='easeInOut'))
                parallel.append(spatial.path.posInterval(0.75, pos, blendType='easeInOut'))
            else:
                pos.y = y - 0.5
                pos.z = -0.5
                parallel.append(spatial.path.hprInterval(0.75, (0, 90, 0), blendType='easeInOut'))
                parallel.append(spatial.path.posInterval(0.75, pos, blendType='easeInOut'))

        return Parallel(*parallel).start()

    def win_level(self):
        if base.endtile_sound:
            base.endtile_sound.play()

        star = False
        num_moves = self.move_counter.value
        if self.level.par is not None:
            if num_moves < self.level.par:
                star = True
                print("Beat level {0} in {1} moves, exceeding requirement for star ({2})!".format(self.level_name, num_moves, self.level.par))
            elif num_moves == self.level.par:
                star = True
                print("Beat level {0} in {1} moves, got star".format(self.level_name, num_moves))
            else:
                print("Beat level {0} in {1} moves ({2} needed for star)".format(self.level_name, num_moves, self.level.par))
        else:
            print("Beat level {0} in {1} moves".format(self.level_name, num_moves))
        base.update_save_state(self.level_name, num_moves, star=star, par=self.level.par)

        self.load_next_level()

    def load_next_level(self):
        if not self.next_levels:
            base.show_level_select()
            return

        level = self.next_levels.pop(0)
        if not level:
            base.show_level_select()
            return

        self.load_level(level)

    def reload_level(self):
        if self.player_control.locked:
            pass

        if base.restart_sound:
            base.restart_sound.play()
        self.load_level(self.level_name)

    def load_level(self, name):
        self.hud.hide()
        self.player_control.lock()
        self.player_control.clear_state()

        level_dir = os.path.join(os.path.dirname(__file__), '..', 'levels')
        level = Level()

        try:
            level.read(os.path.join(level_dir, name + '.lvl'))
        except IOError as ex:
            print("Failed to load level {0}: {1}".format(name, ex))
            return

        self.level = level
        self.level_name = name

        print("Loading level {0}".format(name))

        # Get the current tile that the player is on.
        spatial = self.component_for_entity(self.player, components.Spatial)
        x, y = int(spatial.x), int(spatial.y)
        cur_tile = self.tiles.get((x, y), None)
        if cur_tile is not None:
            del self.tiles[(x, y)]

        self.level_root.wrt_reparent_to(self.old_level_root)
        level_root = self.root.attach_new_node("level")
        self.level_root = level_root

        # Make previous tiles fall away
        #for tile in self.tiles.values():
        #    self.add_component(tile, components.Falling(drag=random() + 0.5))

        self.old_tiles.append(list(self.tiles.values()))
        self.tiles.clear()

        self.teleporters.clear()
        self.toggle_tiles.clear()

        i = 0
        entrance = None
        exit_tile = None
        entrance_tile = None

        for x, y, type in level.get_tiles():
            tile = self.place_tile(x, y, type)
            if type == TileType.exit:
                exit_tile = tile

            if type == TileType.entrance:
                entrance = (x, y)
                entrance_tile = tile

            if type == TileType.teleporter:
                self.teleporters.add((x, y))

            if type == TileType.active or type == TileType.inactive:
                self.toggle_tiles.add((x, y))

            self.tiles[(x, y)] = tile

        # Remove current tile that the player is on; colour the entrance tile
        # the same way
        entrance_tile_path = self.component_for_entity(entrance_tile, components.Spatial).path
        if cur_tile is not None:
            cur_tile_path = self.component_for_entity(cur_tile, components.Spatial).path
            entrance_tile_path.set_color_scale(cur_tile_path.get_color_scale())
            self.delete_entity(cur_tile)

        # Reposition player and the exit tile they rode in on
        self.old_level_root.set_x(self.old_level_root.get_x() + entrance[0] - spatial.x)
        self.old_level_root.set_y(self.old_level_root.get_y() + entrance[1] - spatial.y)
        spatial.x = entrance[0]
        spatial.y = entrance[1]
        level_root.set_z(7)

        die = self.component_for_entity(self.player, components.Die)
        if die.die.top_number != 1:
            # Delay exit tile a little since the cube needs to rotate oddly
            exit_tile_duration = 2.2
        else:
            exit_tile_duration = 2.0

        die_heading = (spatial.path.get_h() + 180) % 360 - 180
        spatial.path.set_h(die_heading)

        #exit_tile_path = self.component_for_entity(self.exit_tile, components.Spatial).path
        #exit_tile_path.wrt_reparent_to(level_root)
        entrance_tile_path.set_h(die_heading)
        entrance_tile_path.set_z(-7)

        level_root.set_z(0)
        self.setup()
        level_root.set_z(7)

        Sequence(
            Parallel(
               self.old_level_root.posInterval(2.0, (self.old_level_root.get_x(), self.old_level_root.get_y(), self.old_level_root.get_z() - 10), blendType='easeOut'),
               entrance_tile_path.posInterval(exit_tile_duration, (entrance_tile_path.get_x(), entrance_tile_path.get_y(), entrance_tile_path.get_z() + 7), blendType='easeOut'),
               level_root.posInterval(2.0, (level_root.get_x(), level_root.get_y(), 0), blendType='easeOut'),
               spatial.path.hprInterval(2.0, (0, 0, 0), blendType='easeInOut'),
               entrance_tile_path.hprInterval(2.0, (0, 0, 0), blendType='easeInOut'),
               entrance_tile_path.colorScaleInterval(2.0, (1, 1, 1, 1), blendType='easeInOut'),
            ),
            Func(self.on_level_start),
        ).start()

    def place_tile(self, x, y, type):
        tile = self.create_entity()

        spatial = components.Spatial("tile", parent=self.level_root, pos=(x, y))
        self.add_component(tile, spatial)
        self.add_component(tile, components.Model(type.get_model(), offset=(0, 0, -0.5), scale=0.98))

        if type.get_model() == "gfx/tile-cracked.bam":
            spatial.path.set_h(randint(0, 3) * 90)
        spatial.path.set_color_scale(type.get_color())
        if type.get_color()[3] < 1.0:
            spatial.path.set_transparency(1)

        symbol = type.get_symbol()
        if symbol:
            self.add_component(tile, components.Symbol(symbol, color=(0.5, 0, 0, 1), font=base.symbol_font))

        if type == TileType.button:
            spatial.path.set_z(0.07)
        elif type == TileType.inactive:
            spatial.path.set_y(y - 0.5)
            spatial.path.set_z(-0.5)
            spatial.path.set_hpr(0, 90, 0)
        elif type == TileType.active:
            spatial.path.set_hpr(0, 0, 0)

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
