from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import LerpFunctionInterval, Func, Sequence, Parallel
from panda3d import core
import esper
import math

from .level import TileType
from . import components


MOUSE_SENSITIVITY = 0.3


class PlayerControl(esper.Processor, DirectObject):
    def __init__(self, player, camera):
        self.player = player
        self.camera = camera

        self.accept('arrow_up', self.move_up)
        self.accept('arrow_down', self.move_down)
        self.accept('arrow_left', self.move_left)
        self.accept('arrow_right', self.move_right)
        self.accept('mouse1', self.start_drag)
        self.accept('mouse1-up', self.stop_drag)
        self.accept('r', self.reload)

        self.locked = True
        self.moving = False
        self.winning_move = False
        self.dragging_pos = None
        self.restore_interval = None
        self.cracked_tile = None
        self.reload = False

    def lock(self):
        # Locks the controls
        self.locked = True
        if self.dragging_pos:
            self.stop_drag()

    def unlock(self):
        self.locked = False
        assert self.world.level

    def reload(self):
        if self.locked:
            return

        self.reload = True

    def start_drag(self):
        if self.restore_interval:
            self.restore_interval.pause()
            self.restore_interval = None

        ptr = base.win.get_pointer(0)
        if ptr.in_window:
            self.dragging_pos = ptr.x, ptr.y

    def stop_drag(self):
        if self.dragging_pos:
            self.dragging_pos = None

            spatial = self.world.component_for_entity(self.camera, components.Spatial)
            self.restore_interval = spatial.path.hprInterval(0.3, spatial.default_hpr, blendType='easeOut')
            self.restore_interval.start()

    def move_up(self):
        if self.locked:
            return
        die = self.world.component_for_entity(self.player, components.Die)
        die.move_up()

    def move_down(self):
        if self.locked:
            return
        die = self.world.component_for_entity(self.player, components.Die)
        die.move_down()

    def move_left(self):
        if self.locked:
            return
        die = self.world.component_for_entity(self.player, components.Die)
        die.move_left()

    def move_right(self):
        if self.locked:
            return
        die = self.world.component_for_entity(self.player, components.Die)
        die.move_right()

    def start_move(self, dir):
        die = self.world.component_for_entity(self.player, components.Die)
        spatial = self.world.component_for_entity(self.player, components.Spatial)

        orig_pos = spatial.path.get_pos()
        orig_quat = spatial.path.get_quat()
        target_pos = spatial.path.get_pos()
        target_quat = spatial.path.get_quat()
        next_number = None
        if dir == 'N':
            target_pos.y += 1
            target_quat *= core.LRotation((1, 0, 0), -90)
            next_number = die.die.north_number
        elif dir == 'E':
            target_pos.x += 1
            target_quat *= core.LRotation((0, 1, 0), 90)
            next_number = die.die.east_number
        elif dir == 'S':
            target_pos.y -= 1
            target_quat *= core.LRotation((1, 0, 0), 90)
            next_number = die.die.south_number
        elif dir == 'W':
            target_pos.x -= 1
            target_quat *= core.LRotation((0, 1, 0), -90)
            next_number = die.die.west_number

        z_scale = math.sqrt(0.5) - 0.5

        x, y = int(target_pos[0]), int(target_pos[1])
        type = self.world.level.get_tile(x, y)
        if not type.is_passable(next_number) and not base.mouseWatcherNode.is_button_down('pause'):
            self.moving = True
            Sequence(
                Parallel(
                    spatial.path.posInterval(0.125, (orig_pos + target_pos) * 0.5, blendType='easeInOut'),
                    LerpFunctionInterval(lambda x: spatial.path.set_z(math.sin(x) * z_scale), 0.125, toData=math.pi * 0.5, blendType='easeInOut'),
                    spatial.path.quatInterval(0.125, (orig_quat + target_quat) * 0.5, blendType='easeInOut'),
                ),
                Parallel(
                    spatial.path.posInterval(0.125, orig_pos, blendType='easeIn'),
                    LerpFunctionInterval(lambda x: spatial.path.set_z(math.sin(x) * z_scale), 0.125, fromData=math.pi * 0.5, toData=0, blendType='easeIn'),
                    spatial.path.quatInterval(0.125, orig_quat, blendType='easeIn'),
                ),
                Func(self.stop_move)).start()
            return False

        if self.cracked_tile:
            # Break away the cracked tile
            self.world.add_component(self.cracked_tile, components.Falling(drag=5.0))
            self.cracked_tile = None

        if type == TileType.exit:
            self.winning_move = True
            self.lock()

        if type == TileType.cracked:
            self.cracked_tile = self.world.tiles[(x, y)]
            self.world.level.remove_tile(x, y)
            del self.world.tiles[(x, y)]

        if dir == 'N':
            die.die.rotate_north()
        elif dir == 'E':
            die.die.rotate_east()
        elif dir == 'S':
            die.die.rotate_south()
        elif dir == 'W':
            die.die.rotate_west()

        self.moving = True

        Sequence(
            Parallel(
                spatial.path.posInterval(0.25, target_pos),
                LerpFunctionInterval(lambda x: spatial.path.set_z(math.sin(x) * z_scale), 0.25, toData=math.pi),
                spatial.path.quatInterval(0.25, target_quat),
            ),
            Func(self.stop_move)).start()

        return True

    def stop_move(self):
        if self.winning_move:
            self.lock()
            self.world.win_level()
            self.winning_move = False

        self.moving = False

    def process(self, dt):
        if self.locked or self.moving:
            return

        die = self.world.component_for_entity(self.player, components.Die)
        spatial = self.world.component_for_entity(self.player, components.Spatial)

        if self.reload:
            self.reload = False
            die.moves.clear()
            self.world.reload_level()
            return

        if self.dragging_pos:
            ptr = base.win.get_pointer(0)
            if ptr.in_window:
                x = (self.dragging_pos[0] - ptr.x) * MOUSE_SENSITIVITY
                y = (self.dragging_pos[1] - ptr.y) * MOUSE_SENSITIVITY
                spatial = self.world.component_for_entity(self.camera, components.Spatial)
                spatial.path.set_hpr(spatial.default_hpr[0] + x, max(min(spatial.default_hpr[1] + y, 0), -90), 0)

        if die.moves:
            if not self.start_move(die.moves.pop(0)):
                die.moves.clear()


class Gravity(esper.Processor):
    def __init__(self, acceleration=1.0):
        self.acceleration = 1.0

    def process(self, dt):
        removed = []

        for ent, (spatial, fall) in self.world.get_components(components.Spatial, components.Falling):
            fall.velocity += self.acceleration * dt * fall.drag

            spatial.path.set_z(spatial.path.get_z() - fall.velocity * dt)

            spatial.path.set_p(spatial.path.get_p() + dt)

            if spatial.path.get_z() < -35:
                removed.append(ent)

        for ent in removed:
            self.world.delete_entity(ent)
