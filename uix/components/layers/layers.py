__all__ = (
    'Layouts', 'BLayout', 'GLayout', 'FLayout',
    'ScrollingLayout', 'ScrollableLabelComponent'
)

from pathlib import Path
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.label import Label
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
    border = ListProperty(None)
    hover_color = ListProperty(None)
    focus_color = ListProperty(None)
    background_color = ListProperty([0, 0, 0, 0])


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
    _isLoading = None
    _animation_loader = None
    _animation_scheduler = None
    color = ListProperty([0, 0, .1, 1])
    text = StringProperty('No Track Playing')
    bar_inactive_color = bar_color = [0, 0, 0, 0]
    effect_cls = ObjectProperty(OpacityScrollEffect)
    restart_time = NumericProperty(20, allownone=True)

    def on_hover(self):
        if self._isLoading is None:
            self._start_animation()

    def _loopTime(self, *_):
        if _:
            return self._view_port.width * 35 / 800
        return self.width * 35 / 800

    def on_text(self, *largs):
        self._view_port.text = largs[1]

    def on_color(self, *largs):
        self._view_port.color = self._view_port.disabled_color = largs[1]

    def _start_animation(self):
        self._unschedule_animation()
        if self._view_port.width < self.width:
            return
        self._isLoading = True
        self._animate(True)

    def _cancel_animation(self):
        if self._isLoading and self._animation_loader:
            self._animation_loader.cancel(self._view_port)
            self._reset_all_props()
            self._view_port.x = 0

    class ScrollableLabel(Label):
        pass

    def __init__(self, **kwargs):
        super(ScrollableLabelComponent, self).__init__(**kwargs)
        self._view_port = self.ScrollableLabel(
            text=self.text, color=self.color, disabled_color=self.color
        )
        self._view_port.bind(texture_size=self._on_texture_update)
        self.add_widget(self._view_port)

    def _schedule_animation(self):
        self._animation_scheduler = Clock.schedule_once(
            lambda *_: self._start_animation(), self.restart_time
        )

    def _unschedule_animation(self):
        if self._animation_scheduler:
            self._animation_scheduler.cancel()
        self._animation_scheduler = None

    def _on_texture_update(self, *_):
        self._cancel_animation()
        self._unschedule_animation()
        self._start_animation()

    def _animate(self, direction=None):
        if direction:
            self._animation_loader = Animation(right=self._view_port.x, d=self._loopTime())
            self._animation_loader.bind(on_complete=self._animation_cycle_complete)
        else:
            self._animation_loader = Animation(x=0, d=self._loopTime(None))
            self._animation_loader.bind(on_complete=self._reset_all_props)
        self._animation_loader.start(self._view_port)

    def _reset_all_props(self, *largs):
        self._isLoading = self._animation_loader = None
        if largs and self.restart_time:
            self._schedule_animation()

    def _animation_cycle_complete(self, *largs):
        largs[1].x = self.width
        self._animation_loader = None
        self._animate()
