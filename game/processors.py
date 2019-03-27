from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import LerpFunctionInterval, Func, Sequence, Parallel
from panda3d import core
import esper
import math

from .level import TileType
from . import components


class PlayerControl(esper.Processor, DirectObject):
    def __init__(self, player):
        self.player = player

        self.accept('arrow_up', self.move_up)
        self.accept('arrow_down', self.move_down)
        self.accept('arrow_left', self.move_left)
        self.accept('arrow_right', self.move_right)

        self.locked = True
        self.moving = False
        self.winning_move = False

    def unlock(self):
        self.locked = False
        assert self.world.level

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

        if type == TileType.exit:
            self.locked = True
            self.winning_move = True

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
            self.locked = True
            self.world.win_level()
            self.winning_move = False

        self.moving = False

    def process(self, dt):
        if self.locked or self.moving:
            return

        die = self.world.component_for_entity(self.player, components.Die)
        spatial = self.world.component_for_entity(self.player, components.Spatial)

        if die.moves:
            if not self.start_move(die.moves.pop(0)):
                die.moves.clear()


class Gravity(esper.Processor):
    def __init__(self, acceleration=1.0):
        self.acceleration = 1.0

    def process(self, dt):
        for ent, (spatial, fall) in self.world.get_components(components.Spatial, components.Falling):
            fall.velocity += self.acceleration * dt * fall.drag

            spatial.path.set_z(spatial.path.get_z() - fall.velocity * dt)

            spatial.path.set_p(spatial.path.get_p() + dt)
