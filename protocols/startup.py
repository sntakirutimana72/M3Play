__all__ = ('routine_001', )

import sys
from os import chdir, environ


def __routine_00A__():
    """ resets some kivy internal configurations for custom reconfigurations to take effects
     .. disables kivy default file logging
     .. disables kivy console logging
     .. exclude kivy environment configuration files
    """
    environ['KIVY_NO_FILELOG'] = '1'
    environ['KIVY_NO_CONSOLELOG'] = '1'
    environ['KIVY_NO_ENV_CONFIG'] = '1'


def __routine_00B__():
    """ when this application is installed inside a operating system environment
        redirect this sys resources pointers to a os-based temp unloaded directory
    """
    if getattr(sys, 'frozen', False):
        chdir(sys._MEIPASS)


def routine_001():
    """ apply new kivy window custom configuration """
    __routine_00A__()
    __routine_00B__()

    from kivy.config import Config
    from utils.cfg import cfg_getter
    from utils.loggers import ilogging
    from pyautogui import size as pysize
    from utils.helpers import stringedArray_2_array

    def _sub_routine(size: str) -> dict:
        sys_size = pysize()
        width, height = stringedArray_2_array(size, int)
        x_axis = str((sys_size[0] - width) // 2)
        y_axis = str((sys_size[1] - height) // 2)

        return {
            'width': width,
            'height': height,
            'minimum_width': width,
            'minimum_height': height,
            'left': x_axis, 'top': y_axis
        }

    try:
        cfg = dict(cfg_getter('WINDOW'))
        cfg_size = cfg['size']
        del cfg['size']
        cfg.update(_sub_routine(cfg_size))

        for option, _ in cfg.items():
            kivy_config_target = 'graphics'
            Config.set(kivy_config_target, option, _)
    except Exception as e:
        ilogging(e)
