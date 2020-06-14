__all__ = ('ilogging', )

from pathlib import Path
from datetime import datetime
from utils.envs import res_dir
from logging import basicConfig, DEBUG, getLogger
    
__logger__ = None


def __setup__():
    global __logger__

    logs_path = Path(res_dir()) / 'Logs'
    if not logs_path.exists():
        try:
            logs_path.mkdir(parents=True)
        except:
            pass

    logfile_name = logs_path.joinpath(datetime.now().strftime('%B-%Y') + '.log')
    basicConfig(filename=logfile_name,
                format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s')
    __logger__ = getLogger('SYAI-M3Play')
    __logger__.setLevel(DEBUG)


def ilogging(message, level: str = 'e'):
    if level == 'i':
        __logger__.info(repr(message))
    elif level == 'e':
        __logger__.error(repr(message))
    elif level == 'd':
        __logger__.debug(repr(message))
    elif level == 'c':
        __logger__.critical(repr(message))
    else:
        __logger__.warning(repr(message))


__setup__()
