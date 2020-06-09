__all__ = ('ImageSourcePath', )

from os import path
from utils.envs import res_dir
from kivy.properties import StringProperty


class ImageSourcePath(object):
    source = StringProperty('')
    icon_name = StringProperty('')

    def on_icon_name(self, _, value):
        icon_full_relative_path = path.join(res_dir(), 'Icons', value)
        if path.isfile(icon_full_relative_path):
            self.source = icon_full_relative_path
        else:
            self.source = ''
