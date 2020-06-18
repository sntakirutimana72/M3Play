import time
import math
from utils.cfg import cfg_getter
from threading import Thread, Lock
from utils.workers import OpsWorker
from protocols.resize import resize
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import mainthread, Clock
from uix.components.layers import BLayout
from utils.loggers import ilogging, elogging
from uix.components.headers import AppHeadBarComponent
from uix.views.playlist import PlaylistManagerComponent
from utils.helpers import strArray_to_tuple, get_metadata
from uix.views.controls import ModularControlsComponent, FooterDisplayComponent


class Keypad_dirs(object):

    def _keypad_closed(self):
        """ This method is called when the keypad instance is released """
        pass

    def __init__(self, **kwargs):
        super(Keypad_dirs, self).__init__(**kwargs)
        self._keypad = None
        Window.bind(on_cursor_enter=self._on_cursor_enter,
                    on_cursor_leave=self._on_cursor_leave
                    )

    def _on_cursor_leave(self, _):
        """ This observes the mouse motion once stepped out of this instance canvas """
        try:
            if self._keypad:
                self._keypad.unbind(on_key_down=self._on_key_down)
                self._keypad = None
        except Exception as e:
            ilogging(e)

    def _on_key_down(self, *largs):
        """ This method listens and dispatches relevant actions in relations to a key event occurred """
        # This keypad-directive toggles playlist-manager
        if largs[2] == 'e' or largs[2] == 'E':
            self._on_toggle_playlist()
            return

        if not self._controls.disabled:
            # This keypad-directive initiates, freezes and resumes a playing activity
            if largs[1][1] == 'spacebar':
                self._on_play_pause(self._controls.play_pause)
                return
            # This keypad-directive changes volume level up and down
            if largs[1][1] in ('up', 'down') and 'ctrl' in largs[3]:
                jump_at = .05 if largs[1][1] == 'up' else -.05
                jump_at += self._controls.volume
                self._controls.vol_display.volume_bar.calculate_from_ratio(jump_at, True)
                return
            # This keypad-directive mutes and un-mutes the modular and the volume controls
            # Although it utilizes the same method to do so with its counter-parts
            if largs[2] == 'm' or largs[2] == 'M':
                self._controls.vol_display.volume_bar.calculate_from_ratio(-1, True)
                return
            # This keypad-directive changes the looping state
            if largs[2] == 'l' or largs[2] == 'L':
                self._on_loop(self._controls.looping)
                return
            # This keypad-directive changes the shuffling state
            if largs[2] == 'r' or largs[2] == 'R':
                self._on_shuffle(self._controls.shuffling)
                return

            if self._is_alive():
                # This keypad-directive stops the playing activity if on
                if largs[2] == 's' or largs[2] == 'S':
                    self._on_stop()
                # This keypad-directive invokes a next routine whereby a next-media available takes turn
                elif largs[2] == 'n' or largs[2] == 'N':
                    self._on_next()
                # This keypad-directive invokes a preview routine whereby a previous-media available takes turn
                elif largs[2] == 'p' or largs[2] == 'P':
                    self._on_previous()
                # This keypad-directive winds and rewinds the playing media 5 sec after and 5 sec before, respectively
                elif largs[1][1] in ('right', 'left') and 'shift' in largs[3]:
                    current_pos, duration = self._current_pos, self._duration
                    jump_at = 5 if largs[1][1] == 'right' else -5
                    jump_at = jump_at / duration + current_pos
                    self._controls.time_display.progress_bar.calculate_from_ratio(jump_at, True)

    def _on_cursor_enter(self, window):
        """ This method observes the mouse motion when it enters this instance canvas """

        if self._keypad is None:
            self._keypad = window.request_keyboard(self._keypad_closed, self)
            self._keypad.bind(on_key_down=self._on_key_down)


class PPlayOnMRestore(object):

    def __init__(self, **kwargs):
        super(PPlayOnMRestore, self).__init__(**kwargs)
        Clock.schedule_once(self._set_mini_restore_observers, 1)

    def _on_restore_play(self, *_):
        if not self._controls.disabled and self._is_alive() and self._state:
            self._on_play_pause(self._controls.play_pause)

    def _on_minimize_pause(self, *_):
        if not self._controls.disabled and self._is_alive() and self._state is None:
            self._on_play_pause(self._controls.play_pause)

    def _set_mini_restore_observers(self, *_):
        Window.bind(
            on_restore=self._on_restore_play,
            on_minimize=self._on_minimize_pause
        )


class M3Play(BLayout, Keypad_dirs, PPlayOnMRestore):
    __events__ = ('on_lap_time', )

    def _resume(self):
        self._modular.play()
        self._flag_all_motion_responses(True)
        Clock.schedule_interval(self._ready_all_tools_from_duration, .01)

    @property
    def playlist(self):
        return self._playlist_manager

    def _get_pos(self):
        try:
            time.sleep(.005)
            while self._is_alive() and not self._state:
                with self._current_pos_lock:
                    @mainthread
                    def _update_current_pos(value):
                        self.dispatch('on_lap_time', value)
                    _update_current_pos(self._modular.get_pos())
                time.sleep(.02)
        finally:
            pass

    def _is_alive(self):
        """ This method checks if the modular is working and its state is either `pause` or `play` """
        return self._modular and (self._modular.state == 'play' or self._state == 'pause')

    def _reset_all(self):
        self._flag_modular()
        self._state = self._current_pos = None
        self._playlist_manager.clear_playingToggle()
        self._options['force'] = False
        self._modular = None

    def _load_next(self):
        """ This method sorts through modular options like loop state and shuffle state,
            and then request another media inline based on all these options states.
            If nothing is available, it invokes a reset routine to return everything to default.
         """
        time.sleep(.2)  # rest a little bit before continuing

        _options = self._options['loop'], self._options['shuffle'], self._loop_ignore
        if not self._playlist_manager.load_next(self._shift_ref, *_options):
            self._reset_all()

        # Resetting :attr:`_go_where` to its default value
        self._shift_ref = 1
        # Resetting :attr:`_loop_ignore` to its default value
        if self._loop_ignore:
            self._loop_ignore = False

    def _set_pause(self):
        self._state = 'pause'
        self._options['force'] = None
        self._controls.play_pause.toggle()

    def _async_stop(self):
        self._flag_all_motion_responses(True)
        with self._current_pos_lock:
            self._modular.stop()
            self._flag_all_motion_responses(False)

    def _run_get_pos(self):
        pos_getter = Thread(target=self._get_pos)
        pos_getter.daemon = True
        pos_getter.start()

    def _now_playing(self):
        metadata = self._metadata
        self._metadata = None
        self._controls.time_display.set_last(self._duration)
        self._footer.display_metadata(metadata)

    def _on_stop(self, *_):
        if self._is_alive():
            self.__stop__(True)

    def _on_next(self, *_):
        if self._is_alive():
            self._loop_ignore = True
            self._async_stop()

    def _prep_modular(self):
        if self._is_alive():
            self.__stop__()

    def do_play(self, source):
        self._prep_modular()
        self.__play__(source)

    def _on_seek(self, *largs):
        self._modular.seek(largs[-1] * self._duration)

    def _on_previous(self, *_):
        if self._is_alive():
            self._shift_ref = -1
            self._loop_ignore = True
            self._async_stop()

    def _on_loop(self, *largs):
        self._options['loop'] = {
            'off': 'All',
            'One': 'off',
            'All': 'One'
        }[self._options['loop']]

        largs[-1].toggle()

    def _on_play_pause(self, *_):
        if self._is_alive():
            state = self._modular.state
            if state == 'stop':
                if self._state == 'pause':
                    self._resume()
                else:
                    self._load_next()
            else:
                self._set_pause()
                self._async_stop()
                self._modular.volume = 0
        else:
            self._load_next()

    def _add_UI_components(self):
        """ This method initiates UI components of the this class instance """
        # Outer Layout
        secondary_layout = BLayout(
            spacing='1dp', padding='2dp', orientation='vertical',
            background_color=self.border
        )
        # Instantiate HeadBar Component
        secondary_layout.add_widget(AppHeadBarComponent())

        # Adding modular-controls to root widget
        self._controls = ModularControlsComponent(
            background_color=self.border,
            on_seek=self._on_seek, on_shuffle=self._on_shuffle,
            on_previous=self._on_previous, on_play_pause=self._on_play_pause,
            on_stop=self._on_stop, on_loop=self._on_loop, on_next=self._on_next
        )
        self._controls.bind(volume=self._on_adjust_volume)
        secondary_layout.add_widget(self._controls)

        # Creating & adding playlist-manager to root widget
        self._playlist_manager = PlaylistManagerComponent(root=self)
        secondary_layout.add_widget(self._playlist_manager)

        # Creating & adding footer-display to root-widget
        self._footer = FooterDisplayComponent(
            on_toggle_playlist=self._on_toggle_playlist,
            on_toggle_size=self._on_toggle_view
        )
        secondary_layout.add_widget(self._footer)
        # Finally add the secondary layer to root itself
        self.add_widget(secondary_layout)

    def _on_toggle_view(self, *_):
        pass

    def on_lap_time(self, *largs):
        """ This trigger-function updates media progress bar """
        if self._is_alive():
            self._current_pos = largs[0] / self._duration
            self._controls.time_display.set_lap(largs[0], self._current_pos)

    def _on_shuffle(self, *largs):
        self._options['shuffle'] = not self._options['shuffle']
        largs[-1].toggle()

    def _set_initial_states(self):
        try:
            colors = []
            for option, value in cfg_getter('MAIN'):
                colors.append(strArray_to_tuple(value))
            self.background_color, self.border = colors
            del colors

            self._options['force'] = False

            for name, state in cfg_getter('MODULAR'):
                if name in ['shuffle', 'loop']:
                    if name == 'shuffle':
                        state = False if state == 'off' else True
                    self._options[name] = state
        except Exception as e:
            ilogging(e)

    def _on_state(self, _, state):
        if self._state is None and state == 'stop':
            self._update_UI_states(state)

            if self._options['force'] is False:
                self._load_next()
            elif self._options['force']:
                self._reset_all()

        elif self._loop_ignore is None:
            self._loop_ignore = False

    def __stop__(self, force=None):
        self._options['force'] = force
        self._async_stop()

    def on_parent(self, _, parent):
        if parent and self._ops_handler is None:
            self._init_ops_handler()

    def _on_toggle_playlist(self, *_):
        """ This method expands & collapses playlist library """
        resize(self.get_root_window())

    def __play__(self, source: object):
        try:
            self._flag_all_motion_responses(True)
            if self._modular is None:
                self._modular = SoundLoader().load(str(source))
                if isinstance(self._modular, SoundLoader) or self._modular is None:
                    raise Exception('Unable to load source file')
                self._flag_modular(True)
            else:
                self._modular.source = str(source)
            self._modular.play()
        except Exception as e:
            ilogging(e)
        finally:
            if isinstance(self._modular, SoundLoader) or self._modular is None:
                elogging()
                self._modular = None
                self._flag_all_motion_responses(False)
            else:
                self._modular.volume = 0
                self._metadata, self._duration = get_metadata(source)
                Clock.schedule_interval(self._ready_all_tools_from_duration, .01)

    def _update_UI_states(self, state):
        self._controls.play_pause.toggle()

        if state == 'play':
            self._options['force'] = False
            self._controls.time_display.activate()
        else:
            self._footer.clear_metadata()
            self._controls.time_display.deactivate()

    def _flag_modular(self, flag=False):
        if flag:
            self._modular.bind(state=self._on_state)
        else:
            self._modular.unbind(state=self._on_state)

    def _on_adjust_volume(self, *largs):
        if self._modular:
            self._modular.volume = largs[1]

    def __init__(self, *largs, **kwargs):
        super(M3Play, self).__init__(**kwargs)
        self.border = None
        self.padding = '1dp'

        self._state = None
        self._options = {}
        self._footer = None
        self._shift_ref = 1
        self._modular = None
        self._metadata = None
        self._controls = None
        self._loop_ignore = None
        self._ops_handler = None
        self._playlist_manager = None

        self._current_pos = None
        self._current_pos_lock = Lock()
        self._duration = None

        self._set_initial_states()
        self._add_UI_components()
        self._init_ops_handler(*largs)

    def _init_ops_handler(self, *cli_inputs):
        self._ops_handler = handler = OpsWorker(root=self)
        self._ops_handler.run()

        if cli_inputs and type(cli_inputs) is tuple:
            _loop = None
            while _loop is None:
                _loop = handler.loop
            _loop.call_soon_threadsafe(handler.submit_startup_load, cli_inputs)

    def _flag_all_motion_responses(self, flag):
        self._controls.disabled = \
            self._footer.disabled = \
            self._playlist_manager.disabled = flag

    def _ready_all_tools_from_duration(self, _):
        length_1, length_2 = self._modular.length, self._duration
        if math.ceil(length_1) >= math.floor(length_2):
            Clock.unschedule(self._ready_all_tools_from_duration)

            if self._state:
                self._on_seek(self._current_pos)
                self._state = None
                self._controls.disabled = False
                self._controls.play_pause.toggle()
                self._controls.disabled = True
            else:
                self._update_UI_states('play')
                self._now_playing()

            self._modular.volume = self._controls.volume
            self._run_get_pos()
            self._flag_all_motion_responses(False)
