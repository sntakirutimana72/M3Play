__all__ = ('BTComponent', 'TextBTComponent', )

from kivy.uix.label import Label
from uix.components.layers import Layouts
from uix.components.behaviors import Clicking, Hovering
from kivy.properties import ListProperty, NumericProperty


class BTComponent(Layouts, Clicking, Hovering):
    background_color = ListProperty([0, 0, 1, .5])
    cover = ListProperty([0, 0, .15, 1])
    shadow = NumericProperty('1dp')


class TextBTComponent(Label, BTComponent):
    color = ListProperty([.2, .2, .2, 1])
    disabled_color = ListProperty([.1, .1, .1, 1])
