__all__ = ('ModularControlsComponent', 'FooterDisplayComponent', )

from pathlib import Path
from kivy.clock import Clock
from kivy.lang import Builder
from utils.cfg import cfg_getter
from kivy.uix.image import AsyncImage
from uix.components.layers import BLayout
from utils.helpers import format_timeframe
from uix.components.behaviors import ImageSourcePath
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty


Builder.load_file(str(Path(__file__).parent / 'controls.kv'))


class FooterDisplayComponent(BLayout):
    __events__ = ('on_toggle_playlist', 'on_toggle_size', )

    class MetadataElement(Screen):
        text = StringProperty('')

    class MetadataComponent(ScreenManager):
        _scheduler = None

        def _animate_metas(self, *_):
            self.next()

        def set_metadata(self, metadata):
            for name in metadata:
                self.add_widget(
                    FooterDisplayComponent.MetadataElement(text=metadata[name], name=name)
                )
            self._scheduler = Clock.schedule_interval(self._animate_metas, 2.25)

        def clear_all(self):
            self._scheduler.cancel()
            self._scheduler = None
            self.clear_widgets()

    def clear_all(self):
        self.ids.album.text = self.ids.artist.text = ''
        self.ids.suffix.text = self.ids.name.text = ''

    def on_toggle_size(self, *_):
        pass

    def on_toggle_playlist(self, *_):
        pass

    def display_metadata(self, data):
        self.ids.album.text = data.album
        self.ids.artist.text = data.artist
        self.ids.suffix.text = data.suffix
        self.ids.name.text = data.name.title()


class TimeCounterComponent(BLayout):
    __events__ = ('on_seek', )

    lap = StringProperty('')
    last = StringProperty('')

    def activate(self):
        self.disabled = False
        bar = self.ids.progress_bar
        bar.calculate_from_ratio(0)
        bar.handle_color[-1] = 1
        bar.cover_color[-1] = .2
        bar.progress_color[-1] = .6

    def deactivate(self):
        self.disabled = True
        bar = self.ids.progress_bar
        bar.calculate_from_ratio(0)
        self.lap = self.last = ''
        bar.handle_color[-1] = bar.progress_color[-1] = bar.cover_color[-1] = 0

    def on_seek(self, *_):
        pass

    def set_last(self, last):
        self.last = format_timeframe(last)

    def set_lap(self, lap, ratio):
        self.lap = format_timeframe(lap)
        self.ids.progress_bar.calculate_from_ratio(ratio)


class VolumeTunerComponent(BLayout):
    volume = NumericProperty(0.)

    class VolStatIconElement(AsyncImage, ImageSourcePath):
        color = [0, 0, .1, .4]

    def on_ids(self, *_):
        self._set_initial_vol()

    def _set_initial_vol(self):
        self.ids.vol_stat.value_ratio = float(cfg_getter('MODULAR', 'volume'))


class ModularControlsComponent(BLayout):
    __events__ = (
        'on_seek', 'on_previous', 'on_shuffle',
        'on_play_pause', 'on_stop', 'on_next', 'on_loop'
    )

    volume = NumericProperty(0.)

    @property
    def looping(self):
        return self.ids.looping

    @property
    def shuffling(self):
        return self.ids.shuffling

    @property
    def play_pause(self):
        return self.ids.p_pause

    def on_seek(self, *_):
        pass

    def on_loop(self, *_):
        pass

    def on_stop(self, *_):
        pass

    def on_next(self, *_):
        pass

    @property
    def time_display(self):
        return self.ids.time_display

    def on_shuffle(self, *_):
        pass

    def on_previous(self, *_):
        pass

    def on_play_pause(self, *_):
        pass
