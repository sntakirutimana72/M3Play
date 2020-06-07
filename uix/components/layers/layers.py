__all__ = (
    'Layouts', 'BLayout', 'GLayout', 'FLayout',
    'ScrollingLayout', 'ScrollableLabelComponent'
)

from pathlib import Path
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from uix.components.behaviors import Hovering
from kivy.effects.opacityscroll import OpacityScrollEffect
from kivy.properties import ListProperty, NumericProperty, ObjectProperty, StringProperty, OptionProperty


Builder.load_file(str(Path(__file__).parent / 'layers.kv'))


class Layouts(Widget):
    border_width = NumericProperty(1)
    hover_color = ListProperty(None)
    focus_color = ListProperty(None)
    background_color = ListProperty([0, 0, 0, 0])
    top_border_color = ListProperty([0, 0, 0, 0])
    down_border_color = ListProperty([0, 0, 0, 0])
    left_border_color = ListProperty([0, 0, 0, 0])
    right_border_color = ListProperty([0, 0, 0, 0])


class ScrollingLayout(ScrollView):
    bar_width = NumericProperty(5)
    bar_color = ListProperty([.23, .23, .2, .5])
    effect_cls = ObjectProperty(OpacityScrollEffect)
    bar_inactive_color = ListProperty([.23, .23, .2, .5])


class BLayout(BoxLayout, Layouts):
    pass


class GLayout(GridLayout, Layouts):
    pass


class FLayout(FloatLayout, Layouts):
    pass


class ScrollableLabelComponent(ScrollView, Hovering):
    __loader__ = None
    __loading__ = None
    __schedule__ = None

    effect_cls = ObjectProperty(OpacityScrollEffect)
    bar_inactive_color = bar_color = [0, 0, 0, 0]

    color = ListProperty([0, 0, .1, 1])
    text = StringProperty('No Track Playing')

    cycleTime = NumericProperty(None, allownone=True)
    mode = OptionProperty('manual', options=('manual', 'auto'))

    def on_mode(self, _, state):
        if state == 'auto':
            if self.children and self.__loading__ is None:
                self.__restart__()
        else:
            if self.children and self.__schedule__:
                self.__unschedule__()

    def __unschedule__(self):
        self.__schedule__.cancel()
        self.__schedule__ = None

    def __reanimate__(self):
        pass

    def __restart__(self):
        view_port = self.children[0]

        if view_port.width < self.width:
            return

        self.__loading__ = True
        loop_time_frame = view_port.width * 35 / 800
        self.__loader__ = Animation(right=view_port.x, d=loop_time_frame)
        self.__loader__.bind(on_complete=self.__complete__)
        self.__loader__.start(view_port)

    def __complete__(self, _, obj):
        obj.x = self.width
        self.__loader__ = None

        loop_time_frame = (self.size[0] * 35 / 800)
        self.__loader__ = Animation(x=0, d=loop_time_frame)
        self.__loader__.bind(on_complete=self.__reset__)
        self.__loader__.start(obj)

    def __animate__(self, state=None):
        pass

    def __reset__(self, *_):
        self.__loading__ = self.__loader__ = None

    def on_hover(self):
        if self.__loading__ is None:
            self.__restart__()

    def __cancel__(self):
        if self.__loading__ and self.__loader__:
            child = self.children[0]
            self.__loader__.cancel(child)
            self.__reset__()
            child.x = 0

    def _on_texture_update(self, *_):
        pass
