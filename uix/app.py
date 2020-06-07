__all__ = ('M3PlayApp', )

from kivy.app import App
from uix.views import M3Play


class M3PlayApp(App):

    def __init__(self, *largs, **kwargs):
        super(M3PlayApp, self).__init__(**kwargs)
        self.root = M3Play(*largs)
