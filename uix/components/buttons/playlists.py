__all__ = ('AudioFileComponent', )

from kivy.lang import Builder
from uix.components.buttons import TextBTComponent
from kivy.properties import ObjectProperty, BooleanProperty


Builder.load_string("""
<AudioFileComponent>:
    bold: True
    shorten: True
    valign: 'middle'
    font_size: '11dp'
    padding: '8dp', 0
    cover: [0, 0, 0, 0]
    size_hint: None, None
    color: [0, 0, .07, 1]
    focus_color: [0, .6, .3, .1]
    hover_color: [.6, .3, 0, .1]
    text_size: self.width, None
    background_color: [0, 0, 0, 0]
    size: '428dp', dp(max(22, self.texture_size[1]))
""")


class AudioFileComponent(TextBTComponent):
    __toggled__ = None
    path = ObjectProperty(None)
    focused = BooleanProperty(False)

    def on_press(self):
        if not self.focused:
            self.__class__.__toggle__(self)
            self._update_UI_on_focus()

    @classmethod
    def getToggled(cls):
        return cls.__toggled__

    def clear_focus(self):
        self._update_UI_on_focus()
        self.focused = False

    @classmethod
    def clearToggle(cls):
        if cls.__toggled__:
            cls.__toggled__.clear_focus()
            cls.__toggled__ = None

    def on_path(self, *largs):
        if largs[1]:
            self.text = largs[1].stem.title()

    def on_hovered(self, *largs):
        self._update_UI_on_hover()

    def _update_UI_on_focus(self):
        hoverTether_state = self.hovered
        if hoverTether_state:
            self.on_hovered()

        self.background_color, self.focus_color = (
            self.focus_color, self.background_color
        )
        if hoverTether_state:
            self.on_hovered()

    def _update_UI_on_hover(self):
        self.background_color, self.hover_color = (
            self.hover_color, self.background_color
        )

    @classmethod
    def __toggle__(cls, toggled_component):
        if cls.__toggled__:
            cls.__toggled__.clear_focus()
        cls.__toggled__ = toggled_component
