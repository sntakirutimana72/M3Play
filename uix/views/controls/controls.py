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
            self.transition.direction = 'down'
            current = self.current
            self.current = {
                'Artist': 'Album',
                'Album': 'Genre',
                'Genre': 'Artist'
            }[current]

        def set_metadata(self, metadata):
            self.clear_widgets()

            for name in ('Artist', 'Album', 'Genre'):
                self.add_widget(
                    FooterDisplayComponent.MetadataElement(
                        text=f'{name}: {metadata[name]}', name=f'{name}'
                    )
                )
            self._scheduler = Clock.schedule_interval(self._animate_metas, 5.8)

        def clear_all(self):
            self._scheduler.cancel()
            self._scheduler = None
            self.clear_widgets()

    def on_toggle_size(self, *_):
        pass

    def on_toggle_playlist(self, *_):
        pass

    def clear_metadata(self):
        self.ids.meta_com.clear_all()
        self.ids.suffix.text = ''
        self.ids.name.text = 'No Track Playing'

    def display_metadata(self, metadata):
        self.ids.name.text = metadata['name'].title()
        self.ids.suffix.text = metadata['suffix'].upper()
        del metadata['name']
        del metadata['suffix']
        self.ids.meta_com.set_metadata(metadata)


class TimeCounterComponent(BLayout):
    __events__ = ('on_seek', )

    lap = StringProperty('')
    last = StringProperty('')

    def activate(self):
        self.disabled = False
        bar = self.progress_bar
        bar.calculate_from_ratio(0)
        bar.handle_color[-1] = 1
        bar.cover_color[-1] = .1
        bar.progress_color[-1] = .6

    def deactivate(self):
        self.disabled = True
        bar = self.progress_bar
        bar.calculate_from_ratio(0)
        self.lap = self.last = ''
        bar.handle_color[-1] = bar.progress_color[-1] = bar.cover_color[-1] = 0

    def on_seek(self, *_):
        pass

    @property
    def progress_bar(self):
        return self.ids.progress_bar

    def set_last(self, last):
        self.last = format_timeframe(last)

    def set_lap(self, lap, ratio):
        self.lap = format_timeframe(lap)
        self.progress_bar.calculate_from_ratio(ratio)


class VolumeTunerComponent(BLayout):
    volume = NumericProperty(0.)

    class VolStatIconElement(AsyncImage, ImageSourcePath):
        color = [0, 0, .1, .4]

    def on_ids(self, *_):
        self._set_initial_vol()

    @property
    def volume_bar(self):
        return self.ids.vol_stat

    def _set_initial_vol(self):
        self.volume_bar.value_ratio = float(cfg_getter('MODULAR', 'volume'))


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
    def vol_display(self):
        return self.ids.vol_display

    @property
    def time_display(self):
        return self.ids.time_display

    def on_shuffle(self, *_):
        pass

    def on_previous(self, *_):
        pass

    def on_play_pause(self, *_):
        pass
