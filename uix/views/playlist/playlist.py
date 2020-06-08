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
    def _get_selected():
        """ Returns a selected media-referee if any available """
        return AudioFileComponent.getToggled()

    def clearToggle(self):
        """ This function clears any selection available from media-referee interfaces """
        AudioFileComponent.clearToggle()

    def load_next(self, *largs):
        """ This shakes a few things to find out which is next on the playlist """

        current_index = self._get_current(largs[0])
        # Resolve next inline when loop state is set to One
        if largs[1] == 'One' and largs[3] is False:
            current_index += 1
        # Resolve when shuffle is disabled but loop has as state one of ['All', 'off']
        elif current_index == len(self.playlist.children) or current_index < 0:
            if largs[1] is None:
                return
            current_index = (len(self.playlist.children) - 1) if (current_index < 0) else 0
        # Resolve when shuffle is enable
        elif largs[2]:
            random.seed(time.time())
            current_index = random.randrange(0, len(self.playlist.children))

        next_track = self._get_next(current_index)
        next_track.dispatch('on_view')
        return True

    def _get_next(self, ix: int):
        """ This function returns the next source-widget at the :attr:`ix' - index. """
        return self.playlist.children[ix]

    def do_play(self, next_inline):
        if next_inline.path.is_file():
            self.root.do_play(next_inline.path)
        else:
            """ Invoke self-removal process """

    def do_select(self, audio_interface):
        pass

    def _get_current(self, go_ward):
        """ This function retrieves a recently playing source-widget if any, and return its index rendered """
        currentObj = PlaylistManagerComponent._get_selected()
        if currentObj:
            return PlaylistManagerComponent._get_index(currentObj, go_ward * -1)
        return len(self.playlist.children) - 1

    @staticmethod
    def _get_index(child, step=0) -> int:
        """ This function finds the index of `child` to the node `parent`, returns another based on :attr:`step` """
        return child.parent.children.index(child) + step
