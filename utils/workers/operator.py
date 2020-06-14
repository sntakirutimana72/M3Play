__all__ = ('OpsWorker', )

import asyncio
from pathlib import Path
from threading import Thread
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.event import EventDispatcher
from utils.helpers import is_format_allowed
from uix.components.buttons import AudioFileComponent


class OpsWorker(EventDispatcher):

    def _create_dropped_submission_task(self, dropped_file):
        self.loop.create_task(self._update_dropped_files(dropped_file))

    def _on_dropping_files(self, _, dropped_file_source):
        """This is an observer-function that processes dropped files to enlist those
            with the allowed extension and reject the rests.
        """
        file_object = OpsWorker._is_allowed(dropped_file_source.decode())

        if file_object:
            self.loop.call_soon_threadsafe(
                self._create_dropped_submission_task, file_object
            )

    async def _update_dropped_files(self, *largs):
        """ This method updates :attr:_dropped_files:`~<class asyncio.Queue>` """

        for file_path in largs:
            if type(file_path) is str:
                file_path = OpsWorker._is_allowed(file_path)
                if file_path is None:
                    continue
            await self._dropped_files.put(file_path)

            if self._adder_pulse is None or self._adder_pulse.done():
                self._adder_pulse = self.loop.create_task(self._add_dropped_to_playlist())

    async def _add_dropped_to_playlist(self):
        """ This method add media file object to a playlist as a UI widget """

        while not self._dropped_files.empty():

            def _is_playlist_ready():
                file_library = self._root.playlist
                if not (file_library and file_library.playlist):
                    return
                return True

            if _is_playlist_ready() is None:
                await asyncio.sleep(.6)
                continue

            @mainthread
            def _add_dropped_file_widget(file_object: object):
                playlist = self._root.playlist
                dropped_uix_interface = AudioFileComponent(
                    path=file_object,
                    on_view=playlist.do_play
                )
                playlist.playlist.add_widget(dropped_uix_interface)

            _media_file_obj = await self._dropped_files.get()
            self._dropped_files.task_done()
            _add_dropped_file_widget(_media_file_obj)

            await asyncio.sleep(.01)

    def submit_startup_load(self, load):
        """ This method injects file-load obtained from cli-argv on startup into the event loop """
        self.loop.create_task(self._update_dropped_files(*load))

    def __init__(self, root):
        super().__init__()
        self._thread_runner = Thread(target=self._start)
        self._thread_runner.daemon = True

        self._dropped_files = asyncio.Queue()
        self._root = root
        self._adder_pulse = None
        self.loop = None

    @staticmethod
    def _is_allowed(source):
        """ This method validate the file source and return a file path object """
        file_object = Path(source)
        if is_format_allowed(file_object) and file_object.exists():
            return file_object

    def _start(self):
        self.loop = asyncio.get_event_loop_policy().new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._run()
        self.loop.run_forever()

    def _run(self):
        """ Bind dropping event on local method
        ... Window.bind(on_dropfile=self._on_dropping_files)
        """
        Window.bind(on_dropfile=self._on_dropping_files)

    def run(self):
        self._thread_runner.start()
