import sys
from os import getenv
from pathlib import Path


def loc_dir():
    PACKAGE = 'SYAI'
    TOOLNAME = '3Play'
    APPDATA = getenv('APPDATA')
    return '.'  # Path(PACKAGE) / APPDATA / TOOLNAME


def res_dir():
    return str(Path(loc_dir()) / 'res')


def exec_dir():
    return '.'  # Path(sys.executable).parent
