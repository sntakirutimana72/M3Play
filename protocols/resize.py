__all__ = ('resize', )

from pyautogui import size as pysize
from kivy.animation import Animation


def resize(window):
    """ This function is only calibrated to work with WINDOW os with task bar at the bottom """

    sys_size = pysize()

    if window.size[1] == 128:
        win_size = window.size[0], 428
        if window.top + 300 > sys_size[1]:
            window.top += 300 - sys_size[1]
    else:
        win_size = window.size[0], 128

    Animation(size=win_size, d=.12).start(window)
