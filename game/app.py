import sys

from direct.showbase.ShowBase import ShowBase
from direct.filter.FilterManager import FilterManager
from panda3d import core
import pman.shim

from .world import World
from .packs import level_packs
from . import ui


class MyFilterManager(FilterManager):
    multisamples = None

    def createBuffer(self, name, xsize, ysize, texgroup, depthbits=1):
        winprops = core.WindowProperties(size=(xsize, ysize))
        props = core.FrameBufferProperties(core.FrameBufferProperties.get_default())
        props.back_buffers = 0
        props.rgb_color = 1
        props.depth_bits = depthbits

        if self.multisamples:
            props.multisamples = self.multisamples

        depthtex, colortex, auxtex0, auxtex1 = texgroup
        buffer = base.graphics_engine.make_output(
            self.win.getPipe(), name, -1,
            props, winprops, core.GraphicsPipe.BF_refuse_window | core.GraphicsPipe.BF_resizeable,
            self.win.getGsg(), self.win)
        if buffer is None:
            return buffer
        if depthtex:
            buffer.add_render_texture(depthtex, core.GraphicsOutput.RTM_bind_or_copy, core.GraphicsOutput.RTP_depth)
        if colortex:
            buffer.add_render_texture(colortex, core.GraphicsOutput.RTM_bind_or_copy, core.GraphicsOutput.RTP_color)
        buffer.set_sort(self.nextsort)
        buffer.disable_clears()
        self.nextsort += 1
        return buffer


class GameApp(ShowBase):
    def __init__(self):
        self.settings = core.load_prc_file(core.Filename.expand_from("$MAIN_DIR/settings.prc"))

        ShowBase.__init__(self, windowType='none')

        # Try opening "gl-version 3 2" window
        props = core.WindowProperties.get_default()
        have_window = False
        try:
            self.open_default_window(props=props)
            have_window = True
        except Exception:
            pass

        if not have_window:
            print("Failed to open window with OpenGL 3.2; falling back to older OpenGL.")
            core.load_prc_file_data("", "gl-version")
            self.open_default_window(props=props)
            print("The window seemed to have opened this time around.")

        gsg = base.win.gsg
        gl_version = (gsg.driver_version_major, gsg.driver_version_minor)
        self.has_fixed_function = gl_version < (3, 2) or \
            gsg.has_extension("GL_ARB_compatibility")

        print("OpenGL version: {0}.{1} ({2})".format(*gl_version, 'compat' if self.has_fixed_function else 'core'))

        # Initialize panda3d-pman
        pman.shim.init(self)

        self.accept('escape', sys.exit)
        self.disable_mouse()

        self.camLens.set_far(50)

        self.set_background_color((0.31, 0.42, 0.53))

        self.symbol_font = loader.load_font("font/FreeSerif.otf")
        self.symbol_font.set_pixels_per_unit(64)

        self.regular_font = loader.load_font("font/Quicksand-Regular.otf")
        self.regular_font.set_pixels_per_unit(64)

        self.title_font = loader.load_font("font/Quicksand-Light.otf")
        self.title_font.set_pixels_per_unit(128)

        self.blur_shader = core.Shader.load(core.Shader.SL_GLSL, "shader/blur.vert", "shader/blur.frag")
        self.blur_scale = core.PTA_float([1.0])

        self.blurred_tex = None

        screen = ui.Screen("select quality")
        ui.Button(screen, 'sublime', pos=(0.0, 0.3), command=self.start_game, extraArgs=[3])
        ui.Button(screen, 'mediocre', pos=(0.0, 0.1), command=self.start_game, extraArgs=[2])
        ui.Button(screen, 'terrible', pos=(0.0, -0.1), command=self.start_game, extraArgs=[1])
        self.quality_screen = screen

    def start_game(self, quality):
        self.quality_screen.hide()
        self.quality = quality

        if quality >= 3:
            MyFilterManager.multisamples = 16
            self.render.set_antialias(core.AntialiasAttrib.M_multisample)

        if quality >= 2:
            self.setup_filters()

        if quality >= 2 or not self.has_fixed_function:
            self.lighting_shader = core.Shader.load(core.Shader.SL_GLSL, 'assets/shader/lighting.vert', 'assets/shader/lighting.frag')
        else:
            self.lighting_shader = None

        self.world = World()
        self.world.root.reparent_to(self.render)

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

        self.accept('escape', self.on_escape)

        self.task_mgr.add(self.process_world)

    def setup_filters(self):
        self.filters = MyFilterManager(base.win, base.cam)
        self.scene_tex = core.Texture()
        self.quad = self.filters.render_scene_into(colortex=self.scene_tex)
        self.quad.clear_color()

        if not self.quad:
            return

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
