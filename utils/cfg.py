__all__ = ('cfg_getter', 'cfg_writer', )

from pathlib import Path
from utils.envs import exec_dir
from configparser import ConfigParser


def cfg_getter(section, option=None):
    try:
        cfg = ConfigParser()
        cfg.read(Path(exec_dir()) / 'setting.ini')
        return cfg.get(section, option) if option else cfg.items(section)
    except:
        pass


def cfg_writer(cfg):
    pass
