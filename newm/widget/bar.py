from abc import abstractmethod
from threading import Thread
import time
import cairo
from pywm import PyWMCairoWidget, PyWMWidgetDownstreamState

from ..interpolation import WidgetDownstreamInterpolation
from ..animate import Animate
from ..config import configured_value

conf_bar_height = configured_value('bar.height', 20)
conf_font_size = configured_value('bar.font-size', 12)

conf_top_bar_text = configured_value('bar.top_texts', lambda: ["1", "2", "3"])
conf_bottom_bar_text = configured_value('bar.bottom_texts', lambda: ["4", "5", "6"])


class Bar(PyWMCairoWidget, Animate):
    def __init__(self, wm):
        PyWMCairoWidget.__init__(
            self, wm,
            int(wm.output_scale * wm.width),
            int(wm.output_scale * conf_bar_height()))
        Animate.__init__(self)

        self.texts = ["Leftp", "Middlep", "Rightp"]
        self.font_size = wm.output_scale * conf_font_size()

    def set_texts(self, texts):
        self.texts = texts
        self.render()

    def _render(self, surface):
        ctx = cairo.Context(surface)

        ctx.set_source_rgba(.0, .0, .0, .7)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()

        ctx.select_font_face('Source Code Pro for Powerline')
        ctx.set_font_size(self.font_size)

        _, y_bearing, c_width, c_height, _, _ = ctx.text_extents("pA")
        c_width /= 2

        total_text_width = sum([len(t) for t in self.texts])
        spacing = self.width - total_text_width * c_width
        spacing /= len(self.texts)

        x = spacing/2.
        for t in self.texts:
            ctx.move_to(x, self.height/2 - c_height/2 - y_bearing)
            ctx.set_source_rgb(1., 1., 1.)
            ctx.show_text(t)
            x += len(t) * c_width + spacing

        ctx.stroke()

    @abstractmethod
    def reducer(self, wm_state):
        pass

    def animate(self, old_state, new_state, dt):
        cur = self.reducer(old_state)
        nxt = self.reducer(new_state)

        self._animate(WidgetDownstreamInterpolation(cur, nxt), dt)

    def process(self):
        return self._process(self.reducer(self.wm.state))


class TopBar(Bar, Thread):
    def __init__(self, wm):
        Bar.__init__(self, wm)
        Thread.__init__(self)

        self._running = True
        self.start()

    def stop(self):
        self._running = False

    def reducer(self, wm_state):
        result = PyWMWidgetDownstreamState()
        result.z_index = 5

        dy = wm_state.top_bar_dy * conf_bar_height()
        result.box = (0, dy - conf_bar_height(), self.wm.width, conf_bar_height())

        return result

    def run(self):
        while self._running:
            self.set()
            time.sleep(1.)

    def set(self):
        self.set_texts(conf_top_bar_text()())

class BottomBar(Bar, Thread):
    def __init__(self, wm):
        Bar.__init__(self, wm)
        Thread.__init__(self)

        self._running = True
        self.start()

    def stop(self):
        self._running = False

    def reducer(self, wm_state):
        result = PyWMWidgetDownstreamState()
        result.z_index = 5

        dy = wm_state.bottom_bar_dy * conf_bar_height()
        result.box = (0, self.wm.height - dy, self.wm.width,
                      conf_bar_height())

        return result

    def run(self):
        while self._running:
            self.set()
            time.sleep(1.)

    def set(self):
        self.set_texts(conf_bottom_bar_text()())
