__all__ = ('ControlBTComponent', 'ControlInterBTComponent', )

from kivy.lang import Builder
from utils.cfg import cfg_getter
from uix.components.buttons import BTComponent
from uix.components.behaviors import ImageSourcePath
from kivy.properties import ListProperty, NumericProperty, StringProperty


Builder.load_string("""
<ControlBTComponent>:
    size_hint_x: None
    width: self.height
    
    canvas:
        Color:
            rgba: root.cover
        Rectangle:
            source: root.source
            pos: self.x + self.shadow, self.y + self.shadow
            size: self.width - self.shadow * 2, self.height - self.shadow * 2
""")


class ControlBTComponent(BTComponent, ImageSourcePath):
    shadow = NumericProperty('3dp')
    cover = ListProperty([0, 0, .1, 1])
    background_color = ListProperty([.15, .15, .12, 0])

    def on_hover(self):
        self.background_color[-1] = .5

    def on_leave(self):
        self.background_color[-1] = 0


class ControlInterBTComponent(ControlBTComponent):
    _benchmark = 'off'
    indicator = StringProperty('full')

    def toggle(self):
        variants = {
            'shuffle': {
                'on': ('shuffle-off.png', 'off'),
                'off': ('shuffle-on.png', 'on')
            }, 'loop': {
                'off': ('loop-all.png', 'All'),
                'All': ('loop-one.png', 'One'),
                'One': ('loop-off.png', 'off')
            }, 'pause_play': {
                'on': ('play.png', 'off'),
                'off': ('pause.png', 'on')
            }
        }
        self.icon_name, self._benchmark = variants[self.indicator][self._benchmark]

    def on_indicator(self, _, state):
        if state == 'shuffle' or state == 'loop':
            self._benchmark = benchmark = cfg_getter('MODULAR', state)

            if state == 'shuffle':
                self._benchmark = 'off' if benchmark == 'on' else 'on'
            elif benchmark == 'off':
                self._benchmark = 'One'
            elif benchmark == 'All':
                self._benchmark = 'off'
            else:
                self._benchmark = 'All'

            self.toggle()
