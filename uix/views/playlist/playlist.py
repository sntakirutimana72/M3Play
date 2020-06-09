__all__ = ('PlaylistManagerComponent', )

import time
import random
from pathlib import Path
from kivy.lang import Builder
from uix.components.layers import BLayout
from kivy.properties import ObjectProperty
from uix.components.behaviors import Hovering
from uix.components.buttons import AudioFileComponent


Builder.load_file(str(Path(__file__).parent / 'playlist.kv'))


class PlaylistManagerComponent(BLayout, Hovering):
    root = ObjectProperty(None)

    @property
    def playlist(self):
        return self.ids.playlist

    @staticmethod
    def _get_playing():
        """ Returns a selected media-referee if any available """
        return AudioFileComponent.getPlayingToggle()

    def load_next(self, *largs):
        """ This shakes a few things to find out which is next on the playlist """

        next_index = self._get_next_playing_index(largs[0])
        # Resolve next inline when loop state is set to One
        if largs[1] == 'One' and largs[3] is False:
            next_index += 1
        # Resolve when shuffle is disabled but loop has as state one of ['All', 'off']
        elif next_index >= len(self.playlist.children) or next_index < 0:
            if largs[1] == 'off':
                return
            next_index = (len(self.playlist.children) - 1) if (next_index < 0) else 0
        # Resolve when shuffle is enable
        elif largs[2]:
            random.seed(time.time())
            next_index = random.randrange(0, len(self.playlist.children) - 1)

        next_audio_object = self.playlist.children[next_index]
        next_audio_object.dispatch('on_view')
        return True

    def clear_playingToggle(self):
        """ This function clears any selection available from media-referee interfaces """
        AudioFileComponent.clearPlayingToggle()

    def do_play(self, next_inline):
        if next_inline.path.is_file():
            self.root.do_play(next_inline.path)
        else:
            """ Invoke self-removal process """

    def _get_next_playing_index(self, go_ward):
        """ This function retrieves a recently playing source-widget if any, and return its index rendered """
        playing_object = PlaylistManagerComponent._get_playing()
        if playing_object:
            parent = playing_object.parent
            return parent.children.index(playing_object) + (go_ward * -1)
        return len(self.playlist.children) - 1
