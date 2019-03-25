import esper
from panda3d import core

from . import die


class Spatial:
    def __init__(self, name="", pos=(0, 0), parent=None):
        self.path = core.NodePath(name)
        self.path.set_pos(pos[0], pos[1], 0)

        if parent is not None:
            self.path.reparent_to(parent)

    def __del__(self):
        self.path.remove_node()

    @property
    def x(self):
        return self.path.get_x()

    @x.setter
    def x(self, x):
        self.path.set_x(x)

    @property
    def y(self):
        return self.path.get_y()

    @y.setter
    def y(self, y):
        self.path.set_y(y)


class Die:
    def __init__(self):
        self.die = die.Die()
        self.moving = False
        self.moves = []

    def move_up(self):
        self.die.rotate_north()
        self.moves.append('N')

    def move_down(self):
        self.die.rotate_south()
        self.moves.append('S')

    def move_left(self):
        self.die.rotate_west()
        self.moves.append('W')

    def move_right(self):
        self.die.rotate_east()
        self.moves.append('E')


class Model:
    def __init__(self, model, offset=None, hpr=None, scale=None):
        self.path = loader.load_model(model)

        if offset is not None:
            self.path.set_pos(offset)

        if hpr is not None:
            self.path.set_hpr(hpr)

        if scale is not None:
            self.path.set_scale(scale)

    def __del__(self):
        self.path.remove_node()


class Camera:
    def __init__(self, camera, pos, look_at=(0, 0, 0), fov=90):
        self.path = camera
        self.path.set_pos(pos)
        self.path.look_at(look_at)

        for cam_node in self.path.find_all_matches("**/+Camera"):
            cam_node.node().get_lens(0).set_fov(fov)
