__all__ = ('AudioFileComponent', )

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from uix.components.buttons import TextBTComponent


Builder.load_string("""
<AudioFileComponent>:
    bold: True
    shorten: True
    valign: 'middle'
    font_size: '11dp'
    padding: '8dp', 0
    cover: (0, 0, 0, 0)
    size_hint: None, None
    color: (0, 0, .05, 1)
    disabled_color: self.color
    text_size: self.width, None
    background_color: (0, 0, 0, 0)
    size: '428dp', dp(max(22, self.texture_size[1]))
""")


class AudioFileComponent(TextBTComponent):
    _selectToggle = None
    _nowPlayingToggle = None
    path = ObjectProperty(None)

    focus_color = (0, .6, .3, .1)
    hover_color = (.6, .3, 0, .1)
    now_playing_color = (1, .2, .2, .1)
            
    def on_view(self, *_):
        if not AudioFileComponent._is_playing(self):
            AudioFileComponent._toggle_playing(self)
            self._on_playing_state()

    def on_press(self, *_):
        AudioFileComponent._toggle_selection(self)
        if AudioFileComponent._is_selected(self):
            self._on_selection_shift()

    @classmethod
    def _is_playing(cls, el):
        return cls._nowPlayingToggle and cls._nowPlayingToggle == el

    def clearSelection(self):
        self._on_selection_shift()

    @classmethod
    def _is_selected(cls, el):
        return cls._selectToggle and cls._selectToggle == el

    def on_path(self, *largs):
        if largs[1]:
            self.text = largs[1].stem.title()

    @classmethod
    def getPlayingToggle(cls):
        return cls._nowPlayingToggle

    @classmethod
    def clearSelectToggle(cls):
        if cls._selectToggle:
            cls._selectToggle.clearSelection()
            cls._selectToggle = None

    @classmethod
    def clearPlayingToggle(cls):
        if cls._nowPlayingToggle:
            cls._nowPlayingToggle.clearPlayingState()
            cls._nowPlayingToggle = None

    def clearPlayingState(self):
        self._on_playing_state()

    def _on_playing_state(self):
        is_selected = AudioFileComponent._is_selected(self)
        is_hovered = self.hovered

        if is_selected:
            self._on_selection_shift()
        if is_hovered:
            self._on_hovering_change()

        self.background_color, self.now_playing_color = (
            self.now_playing_color, self.background_color
        )
        if is_hovered:
            self._on_hovering_change()
        if is_selected:
            self._on_selection_shift()

    def on_hovered(self, *largs):
        self._on_hovering_change()

    def _on_selection_shift(self):
        is_hovered = self.hovered
        if is_hovered:
            self._on_hovering_change()

        self.background_color, self.focus_color = (
            self.focus_color, self.background_color
        )
        if is_hovered:
            self._on_hovering_change()

    def _on_hovering_change(self):
        self.background_color, self.hover_color = (
            self.hover_color, self.background_color
        )

    @classmethod
    def _toggle_playing(cls, playing_component):
        if cls._nowPlayingToggle:
            cls._nowPlayingToggle.clearPlayingState()
        cls._nowPlayingToggle = playing_component

    @classmethod
    def _toggle_selection(cls, toggled_component):
        if cls._selectToggle:
            cls._selectToggle.clearSelection()
            if cls._selectToggle == toggled_component:
                cls._selectToggle = None
                return
        cls._selectToggle = toggled_component
