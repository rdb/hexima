__all__ = ['Panel', 'Button']

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
import direct.gui.DirectGuiGlobals as DGG
from direct.interval.IntervalGlobal import LerpFunctionInterval, Func, Sequence, Parallel
from panda3d import core
from random import random


BORDER_WIDTH = 0.005
UI_COLOR = (1, 1, 1, 1)


def generate_border(path, frame):
    cm = core.CardMaker("border")
    cm.set_frame(frame[0] - BORDER_WIDTH, frame[0], frame[2] - BORDER_WIDTH, frame[3] + BORDER_WIDTH)
    border = path.attach_new_node(cm.generate())
    border.set_shader_off(1)
    border.set_color_scale_off(1)

    cm.set_frame(frame[1], frame[1] + BORDER_WIDTH, frame[2] - BORDER_WIDTH, frame[3] + BORDER_WIDTH)
    border = path.attach_new_node(cm.generate())
    border.set_shader_off(1)
    border.set_color_scale_off(1)

    cm.set_frame(frame[0] - BORDER_WIDTH, frame[1] + BORDER_WIDTH, frame[2] - BORDER_WIDTH, frame[2])
    border = path.attach_new_node(cm.generate())
    border.set_shader_off(1)
    border.set_color_scale_off(1)

    cm.set_frame(frame[0] - BORDER_WIDTH, frame[1] + BORDER_WIDTH, frame[3], frame[3] + BORDER_WIDTH)
    border = path.attach_new_node(cm.generate())
    border.set_shader_off(1)
    border.set_color_scale_off(1)


class Panel:
    def __init__(self, parent, frame=None, pos=(0, 0), anchor=None, title=""):
        text_pos = ((frame[1] + frame[0]) * 0.5, frame[3] - 0.1)
        self.path = DirectFrame(frameSize=frame, relief=None, parent=parent.path, text=title, text_scale=0.09, text_align=core.TextNode.A_center, text_fg=UI_COLOR, text_pos=text_pos, text_font=base.regular_font)
        generate_border(self.path, frame)

        #if anchor is None:
        #    self.path.reparent_to(base.aspect2d)
        #else:
        #    self.path.reparent_to(getattr(base, 'a2d' + anchor))

        #self.path.set_shader(base.blur_shader)
        #self.path.set_shader_input("image", base.blurred_tex)
        #self.path.set_shader_input("direction", (1, 1))
        #self.path.set_color_scale((0.8, 0.8, 0.8, 1.0))


class LevelButton:
    font = None

    def __init__(self, parent, number=1, pos=(0, 0), command=None, extraArgs=[], locked=False):
        if LevelButton.font is None:
            LevelButton.font = loader.load_font('font/font-awesome5.otf')

        text = '⚀⚁⚂⚃⚄⚅'[number - 1]
        self.path = DirectButton(parent=parent.path, text_fg=UI_COLOR, text_font=base.symbol_font, relief=None, text=text, scale=0.07, text_scale=2, pos=(pos[0], 0, pos[1]), command=command, extraArgs=extraArgs)

        #text = ''[number - 1]
        #self.path = DirectButton(parent=parent.path, text_fg=UI_COLOR, text_font=self.font, relief=None, text=text, scale=0.07, pos=(pos[0], 0, pos[1]))
        self.path.set_shader_off(1)
        self.path.set_color_scale_off(1)

        if locked:
            self.path.set_color_scale((1, 1, 1, 0.5))

            self.text = OnscreenText(parent=self.path, text='', font=self.font, scale=0.7, pos=(0.28, -0.08), fg=UI_COLOR)
            self.text.set_color_scale((1, 1, 1, 1), 2)


class Button:
    def __init__(self, parent, text="", pos=(0, 0), size=(0.4, 0.2)):
        #frame = (-size[0] * 0.5, size[0] * 0.5, -size[1] * 0.5, size[1] * 0.5)
        frame = (-0.15, 0.15, -0.03, 0.08)
        self.path = DirectButton(parent=parent.path, text_fg=UI_COLOR, relief=None, frameSize=frame, text=text, text_scale=0.09, pos=(pos[0], 0, pos[1]))
        generate_border(self.path, frame)

        self.path.set_shader_off(1)
        self.path.set_color_scale_off(1)


class Screen:
    def __init__(self, title=""):
        self.path = OnscreenText(text=title, scale=0.2, pos=(0, 0.5), fg=UI_COLOR, font=base.title_font)

        cm = core.CardMaker("card")
        cm.set_frame_fullscreen_quad()
        card = render2d.attach_new_node(cm.generate())
        card.set_shader(base.blur_shader)
        card.set_shader_input("image", base.blurred_tex)
        card.set_shader_input("direction", (4, 0))
        card.set_shader_input("scale", base.blur_scale)
        card.set_transparency(1)
        self.blur_card = card

        cm = core.CardMaker("card")
        cm.set_frame_fullscreen_quad()
        card = render2d.attach_new_node(cm.generate())
        card.set_color(core.LColor(base.win.clear_color.xyz, 0.5))
        card.set_transparency(1)
        card.set_bin('fixed', 40)
        self.fade_card = card

    def show(self):
        duration = 0.5
        Sequence(
            Func(self.blur_card.show),
            Func(self.fade_card.show),
            Parallel(
                LerpFunctionInterval(lambda x: base.blur_scale.set_element(0, x), duration, fromData=0.0, toData=1.0),
                LerpFunctionInterval(lambda x: self.blur_card.set_alpha_scale(x), duration, fromData=0.0, toData=1.0),
                LerpFunctionInterval(lambda x: self.fade_card.set_alpha_scale(x), duration, fromData=0.0, toData=0.5),
            ),
            Func(self.path.show),
        ).start()

    def hide(self):
        duration = 0.5
        Sequence(
            Parallel(
                LerpFunctionInterval(lambda x: base.blur_scale.set_element(0, x), duration, toData=0.0, fromData=1.0),
                LerpFunctionInterval(lambda x: self.blur_card.set_alpha_scale(x), duration, toData=0.0, fromData=1.0),
                LerpFunctionInterval(lambda x: self.fade_card.set_alpha_scale(x), duration, toData=0.0, fromData=0.5),
            ),
            Func(self.blur_card.hide),
            Func(self.fade_card.hide),
        ).start()
        self.path.hide()
