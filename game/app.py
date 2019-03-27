import sys

from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from panda3d import core
import pman.shim

from .world import World
from . import ui


level_packs = [
    ("one", ["level0", "level1", "level2", "level3", "level4", "level5"]),
    ("two", ["level6", "level7", "level8"]),
    ("three", []),
    ("four", []),
    ("five", []),
    ("six", []),
]


class GameApp(ShowBase):
    def __init__(self):
        self.settings = core.load_prc_file(core.Filename.expand_from("$MAIN_DIR/settings.prc"))

        ShowBase.__init__(self)
        pman.shim.init(self)
        self.accept('escape', self.on_escape)
        self.disable_mouse()

        self.set_background_color((0.31, 0.42, 0.53))

        self.symbol_font = loader.load_font("font/FreeSerif.otf")
        self.symbol_font.set_pixels_per_unit(64)

        self.regular_font = loader.load_font("font/Quicksand-Regular.otf")
        self.regular_font.set_pixels_per_unit(64)

        self.title_font = loader.load_font("font/Quicksand-Light.otf")
        self.title_font.set_pixels_per_unit(64)

        self.world = World()
        self.world.root.reparent_to(self.render)

        self.blur_shader = core.Shader.load(core.Shader.SL_GLSL, "shader/blur.vert", "shader/blur.frag")
        self.blur_scale = core.PTA_float([1.0])

        self.setup_filters()

        num_packs = len(level_packs)
        x = (num_packs - 1) * -0.2

        screen = ui.Screen("level select")
        for pack_name, levels in level_packs:
            while len(levels) < 6:
                levels.append(None)
            panel = ui.Panel(screen, (-0.15, 0.15, -0.25, 0.25), title=pack_name)

            y = 0
            for l, r in (1, 2), (3, 4), (5, 6):
                ui.LevelButton(panel, l, (-0.05, y), command=self.on_switch_level, extraArgs=[pack_name, l-1], locked=not levels[l-1])
                ui.LevelButton(panel, r, (0.05, y), command=self.on_switch_level, extraArgs=[pack_name, r-1], locked=not levels[r-1])
                y -= 0.1

            panel.path.set_x(x)
            x += 0.4

        ui.Button(screen, 'back', pos=(-0.2, -0.5))
        self.level_select = screen

        self.task_mgr.add(self.process_world)

        self.accept('f3', self.world.win_level)

    def setup_filters(self):
        self.filters = FilterManager(base.win, base.cam)
        self.scene_tex = core.Texture()
        self.quad = self.filters.render_scene_into(colortex=self.scene_tex)
        self.quad.clear_color()

        prev_tex = self.scene_tex

        intermediate_tex = core.Texture()
        intermediate_tex.set_minfilter(core.Texture.FT_linear)
        intermediate_tex.set_magfilter(core.Texture.FT_linear)
        intermediate_quad = self.filters.render_quad_into("blur-x", colortex=intermediate_tex)
        intermediate_quad.set_shader_input("image", prev_tex)
        intermediate_quad.set_shader_input("direction", (2, 0))
        intermediate_quad.set_shader_input("scale", self.blur_scale)
        intermediate_quad.set_shader(self.blur_shader)
        prev_tex = intermediate_tex

        intermediate_tex = core.Texture()
        intermediate_tex.set_minfilter(core.Texture.FT_linear)
        intermediate_tex.set_magfilter(core.Texture.FT_linear)
        intermediate_quad = self.filters.render_quad_into("blur-y", colortex=intermediate_tex)
        intermediate_quad.set_shader_input("image", prev_tex)
        intermediate_quad.set_shader_input("direction", (0, 2))
        intermediate_quad.set_shader_input("scale", self.blur_scale)
        intermediate_quad.set_shader(self.blur_shader)
        prev_tex = intermediate_tex

        intermediate_tex = core.Texture()
        intermediate_tex.set_minfilter(core.Texture.FT_linear)
        intermediate_tex.set_magfilter(core.Texture.FT_linear)
        intermediate_quad = self.filters.render_quad_into("blur-y", colortex=intermediate_tex)
        intermediate_quad.set_shader_input("image", prev_tex)
        intermediate_quad.set_shader_input("direction", (0, 4))
        intermediate_quad.set_shader_input("scale", self.blur_scale)
        intermediate_quad.set_shader(self.blur_shader)
        prev_tex = intermediate_tex

        self.blurred_tex = prev_tex

    def on_escape(self):
        self.level_select.show()

    def on_switch_level(self, pack_name, li):
        pack = dict(level_packs)[pack_name]
        if li >= len(pack):
            return

        level = pack[li]
        if not level:
            return

        self.world.load_level(level)
        self.world.next_levels = pack[li + 1:]
        self.level_select.hide()

    def __del__(self):
        core.unload_prc_file(self.settings)

    def process_world(self, task):
        self.world.process(globalClock.dt)
        return task.cont
