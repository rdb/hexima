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
        self.moves.append('N')

    def move_down(self):
        self.moves.append('S')

    def move_left(self):
        self.moves.append('W')

    def move_right(self):
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

    def setup(self, world, ent):
        spatial = world.component_for_entity(ent, Spatial)
        self.path.reparent_to(spatial.path)


class Camera:
    def __init__(self, camera, pos, look_at=(0, 0, 0), fov=90):
        self.path = camera
        self.path.set_pos(pos)
        self.path.look_at(look_at)

        for cam_node in self.path.find_all_matches("**/+Camera"):
            cam_node.node().get_lens(0).set_fov(fov)

    def setup(self, world, ent):
        spatial = world.component_for_entity(ent, Spatial)
        self.path.reparent_to(spatial.path)


class Compass:
    def __init__(self, reference=None, properties='xyzrs'):
        self.reference = reference
        self.properties = properties

    def setup(self, world, ent):
        spatial = world.component_for_entity(ent, Spatial)
        if self.reference is None:
            reference = core.NodePath()
        else:
            reference = world.component_for_entity(self.reference, Spatial).path

        props = 0
        if 'x' in self.properties:
            props |= core.CompassEffect.P_x
        if 'y' in self.properties:
            props |= core.CompassEffect.P_y
        if 'z' in self.properties:
            props |= core.CompassEffect.P_z
        if 'r' in self.properties:
            props |= core.CompassEffect.P_rot
        if 's' in self.properties:
            props |= core.CompassEffect.P_scale
        spatial.path.set_effect(core.CompassEffect.make(reference, props))


class Sun:
    def __init__(self, direction, color=None, color_temperature=None, intensity=None):
        self.light = core.DirectionalLight("sun")

        q = core.Quat()
        core.look_at(q, direction)
        self.light.set_transform(core.TransformState.make_quat(q))
        self.path = None

        if color is not None:
            self.light.set_color(color)
        if color_temperature is not None:
            self.light.set_color_temperature(color_temperature)
        if intensity is not None:
            self.light.set_color(self.light.get_color() * intensity)

        self.light.set_shadow_caster(True, 1024, 1024)

    def setup(self, world, ent):
        path = world.root.attach_new_node(self.light)
        world.root.set_light(path)
        shader = core.Shader.load(core.Shader.SL_GLSL, 'assets/shader/lighting.vert', 'assets/shader/lighting.frag')
        world.root.set_shader(shader)
        world.root.set_depth_offset(-2)

        bmin, bmax = world.root.get_tight_bounds(path)
        lens = self.light.get_lens()
        lens.set_film_offset((bmin.xz + bmax.xz) * 0.5)
        lens.set_film_size(bmax.xz - bmin.xz)
        lens.set_near_far(bmin.y, bmax.y)


class Symbol:
    def __init__(self, text="", font=None, color=None):
        self.node = core.TextNode("")
        self.node.text = text
        self.node.align = core.TextNode.A_center

        if font is not None:
            self.node.font = font

        if color is not None:
            self.node.text_color = color

    def setup(self, world, ent):
        spatial = world.component_for_entity(ent, Spatial)
        path = spatial.path.attach_new_node(self.node)
        path.set_shader_off(1)
        path.set_light_off(1)
        path.set_hpr(0, -90, 0)
        path.set_pos(0, -0.3, -0.499)
