import time
from utils.cfg import cfg_getter
from threading import Thread, Lock
from utils.workers import OpsWorker
from protocols.resize import resize
from kivy.core.audio import SoundLoader
from kivy.clock import mainthread, Clock
from uix.components.layers import BLayout
from utils.loggers import ilogging, elogging
from utils.helpers import stringedArray_2_array
from uix.components.headers import AppHeadBarComponent
from uix.views.playlist import PlaylistManagerComponent
from uix.views.controls import ModularControlsComponent, FooterDisplayComponent


class keypad_routine(object):
    pass


class minimize_routine(object):
    pass


class M3Play(BLayout, keypad_routine, minimize_routine):
    __events__ = ('on_lap_time', )

    def _resume(self):
        self._modular.play()
        Clock.schedule_interval(self._ready_all_tools_from_duration, .01)

    def _run_get_pos(self):
        pos_getter = Thread(target=self._get_pos)
        pos_getter.daemon = True
        pos_getter.start()

    def _on_duration(self, value):
        self._duration = value
        self._controls.time_display.set_last(value)

    @property
    def playlist(self):
        return self._playlist_manager

    def _get_pos(self):
        try:
            while self._is_alive() and not self._state:
                with self._current_pos_lock:
                    @mainthread
                    def _update_current_pos(value):
                        self.dispatch('on_lap_time', value)
                    _update_current_pos(self._modular.get_pos())
                time.sleep(.02)
        finally:
            pass

    def _on_next(self):
        if self._is_alive():
            self._loop_ignore = True
            self._async_stop()

    def _is_alive(self):
        """ This method checks if the modular is working and its state is either `pause` or `play` """
        return self._modular and (self._modular.state == 'play' or self._state == 'pause')

    def _reset_all(self):
        self._flag_modular()
        self._state = self._current_pos = None
        self._playlist_manager.clearToggle()
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
        self._shift_ref = -1
        # Resetting :attr:`_loop_ignore` to its default value
        if self._loop_ignore:
            self._loop_ignore = False

    def _set_pause(self):
        self._state = 'pause'
        self._options['force'] = None

    def _async_stop(self):
        self._flag_all_controls(True)
        with self._current_pos_lock:
            self._flag_all_controls(False)
            self._modular.stop()

    def _on_stop(self, *_):
        if self._is_alive():
            self.__stop__(True)

    def _on_previous(self):
        if self._is_alive():
            self._shift_ref = 1
            self._loop_ignore = True
            self._async_stop()

    def do_play(self, source):
        self._prep_modular()
        self.__play__(source)

    def _prep_modular(self):
        if self._is_alive():
            self.__stop__()

    def _on_seek(self, *largs):
        self._modular.seek(largs[-1] * self._duration)

    def _on_loop(self, *largs):
        self._options['loop'] = {
            'off': 'All',
            'One': 'off',
            'All': 'One'
        }[self._options['loop']]

        largs[-1].toggle()

    def __play__(self, source):
        try:
            self._flag_all_controls(True)
            if self._modular is None:
                self._modular = SoundLoader().load(source)
                if isinstance(self._modular, SoundLoader):
                    raise Exception('Unable to load source file')
                self._flag_modular(True)
            else:
                self._modular.source = source
            self._modular.play()
        except Exception as e:
            ilogging(e)
        finally:
            if isinstance(self._modular, SoundLoader):
                elogging()
                self._modular = None
                self._flag_all_controls(False)
            else:
                self._modular.volume = 0
                Clock.schedule_interval(self._ready_all_tools_from_duration, .01)

    def _ready_all_tools_from_duration(self, _):
        duration = self._modular.length
        if type(duration) is float and duration > 0:
            Clock.unschedule(self._ready_all_tools_from_duration)

            if self._state:
                self._on_seek(self._current_pos)
                self._state = None
            else:
                self._update_UI_states('play')
                self._on_duration(duration)

            self._modular.volume = self._controls.volume
            self._run_get_pos()
            self._flag_all_controls(False)

    def _flag_all_controls(self, flag):
        self._controls.disabled = self._footer.disabled = flag

    def _add_UI_components(self):
        """ This method initiates UI components of the this class instance """
        # Instantiate HeadBar Component
        self.add_widget(AppHeadBarComponent())
        # Adding modular-controls to root widget
        self._controls = ModularControlsComponent(
            background_color=self.background_color,
            on_seek=self._on_seek, on_shuffle=self._on_shuffle,
            on_previous=self._on_previous, on_play_pause=self._on_play_pause,
            on_stop=self._on_stop, on_loop=self._on_loop, on_next=self._on_next
        )
        self._controls.bind(volume=self._on_adjust_volume)
        self.add_widget(self._controls)
        # Creating & adding playlist-manager to root widget
        self._playlist_manager = PlaylistManagerComponent(root=self)
        self.add_widget(self._playlist_manager)
        # Creating & adding footer-display to root-widget
        self._footer = FooterDisplayComponent(
            on_toggle_playlist=self._on_toggle_playlist,
            on_toggle_size=self._on_toggle_view
        )
        self.add_widget(self._footer)

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
            self.background_color = stringedArray_2_array(
                cfg_getter('MAIN', 'background')
            )
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

    def _on_toggle_playlist(self, _):
        resize(self.get_root_window())

    def _on_play_pause(self, *largs):
        if self._is_alive():
            state = self._modular.state
            if state == 'stop':
                if self._state == 'pause':
                    self._resume()
                else:
                    self._load_next()
            else:
                self._flag_all_controls(True)
                self._set_pause()
                self._async_stop()
                self._modular.volume = 0
                self._flag_all_controls(False)
        else:
            self._load_next()

    def _update_UI_states(self, state):
        self._controls.play_pause.toggle()

        if state == 'play':
            self._options['force'] = False
            self._controls.time_display.activate()
        else:
            self._controls.time_display.deactivate()

    def _flag_modular(self, flag=False):
        if flag:
            self._modular.bind(state=self._on_state)
        else:
            self._modular.unbind(state=self._on_state)

    def _on_adjust_volume(self, *largs):
        if self._modular:
            self._modular.volume = largs[-1]

    def __init__(self, *largs, **kwargs):
        super(M3Play, self).__init__(**kwargs)
        self.padding = ('2dp', 0, '2dp', '2dp')
        self.orientation = 'vertical'
        self.spacing = '1dp'

        self._state = None
        self._options = {}
        self._footer = None
        self._shift_ref = -1
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