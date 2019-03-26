from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import LerpFunctionInterval, Func, Sequence, Parallel
from panda3d import core
import esper
import math

from . import components


class Movement(esper.Processor):
    def process(self, dt):
        # I want to rethink this...
        for ent, (model, spatial) in self.world.get_components(components.Model, components.Spatial):
            model.path.reparent_to(spatial.path)


class PlayerControl(esper.Processor, DirectObject):
    def __init__(self, player):
        self.player = player

        self.accept('arrow_up', self.move_up)
        self.accept('arrow_down', self.move_down)
        self.accept('arrow_left', self.move_left)
        self.accept('arrow_right', self.move_right)

        self.moving = False

    def move_up(self):
        die = self.world.component_for_entity(self.player, components.Die)
        die.move_up()

    def move_down(self):
        die = self.world.component_for_entity(self.player, components.Die)
        die.move_down()

    def move_left(self):
        die = self.world.component_for_entity(self.player, components.Die)
        die.move_left()

    def move_right(self):
        die = self.world.component_for_entity(self.player, components.Die)
        die.move_right()

    def start_move(self, dir):
        die = self.world.component_for_entity(self.player, components.Die)
        spatial = self.world.component_for_entity(self.player, components.Spatial)

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

        x, y = int(target_pos[0]), int(target_pos[1])
        if self.world.level.check_obstacle(x, y, next_number):
            return False

        if dir == 'N':
            die.die.rotate_north()
        elif dir == 'E':
            die.die.rotate_east()
        elif dir == 'S':
            die.die.rotate_south()
        elif dir == 'W':
            die.die.rotate_west()
        print(die.die.top_number)

        self.moving = True

        z_scale = math.sqrt(0.5) - 0.5
        Sequence(
            Parallel(
                spatial.path.posInterval(0.25, target_pos),
                LerpFunctionInterval(lambda x: spatial.path.set_z(math.sin(x) * z_scale), 0.25, toData=math.pi),
                spatial.path.quatInterval(0.25, target_quat),
            ),
            Func(self.stop_move)).start()

        return True

    def stop_move(self):
        self.moving = False

    def process(self, dt):
        if self.moving:
            return

        die = self.world.component_for_entity(self.player, components.Die)
        spatial = self.world.component_for_entity(self.player, components.Spatial)

        if die.moves:
            if not self.start_move(die.moves.pop(0)):
                die.moves.clear()
