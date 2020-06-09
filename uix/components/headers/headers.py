__all__ = ('HeadBarComponent', 'AppHeadBarComponent', )

from kivy.app import App
from pathlib import Path
from kivy.lang import Builder
from utils.cfg import cfg_getter
from kivy.uix.label import Label
from utils.loggers import ilogging
from kivy.uix.widget import Widget
from protocols.resize import resize
from kivy.uix.boxlayout import BoxLayout
from uix.components.layers import BLayout
from utils.helpers import stringedArray_2_array
from uix.components.behaviors import Dragging, Hovering
from kivy.properties import NumericProperty, StringProperty, ListProperty, OptionProperty


Builder.load_file(str(Path(__file__).parent / 'headers.kv'))


class TitleElement(Label):
    pass


class GraffitiFeature(Widget):
    pass


class AppControlsContainer(BoxLayout, Hovering):
    toggle_graffiti = NumericProperty(.5)
    graffiti_color = ListProperty([.1, .1, .3])
    disable_controls = OptionProperty('', options=['', '&ri', '&mi', 'mi&ri'])

    def on_hover(self):
        self.toggle_graffiti = 1

    def on_leave(self):
        self.toggle_graffiti = .5

    def on_close(self):
        self.parent.dispatch('on_close')

    def on_resize(self):
        self.parent.dispatch('on_resize')

    def on_minimize(self):
        self.parent.dispatch('on_minimize')

    def on_disable_controls(self, _, disabler):
        if disabler in ['&ri', 'mi&ri']:
            self.ids.resize.disabled = True
        elif disabler in ['&mi', 'mi&ri']:
            self.ids.minimize.disabled = True


class HeadBarComponent(BLayout, Dragging):
    __events__ = ('on_close', 'on_resize', 'on_minimize', )

    draggable_obj = 'layer'
    title = StringProperty('')
    title_color = ListProperty([1, 1, 1, 1])
    graffiti_color = ListProperty([0, 0, .1])
    background_color = ListProperty([0, 0, 0, 0])
    disable_controls = OptionProperty('', options=['', '&ri', '&mi', 'mi&ri'])

    def __init__(self, **kwargs):
        super(HeadBarComponent, self).__init__(**kwargs)
        self._set_initial_states()

    def _set_initial_states(self):
        pass

    def on_close(self):
        pass

    def on_resize(self):
        pass

    def on_minimize(self):
        pass


class AppHeadBarComponent(HeadBarComponent):
    draggable_obj = 'app'

    def _set_initial_states(self):
        try:
            configs = dict(cfg_getter('HEADER'))
            self.title = configs['title']
            self.title_color = stringedArray_2_array(configs['color'])
            self.background_color = stringedArray_2_array(configs['background'])
        except Exception as e:
            ilogging(e)

    def on_minimize(self):
        App.get_running_app().root_window.minimize()

    def on_resize(self):
        resize(App.get_running_app().root_window)

    def on_close(self):
        App.stop(App.get_running_app())
