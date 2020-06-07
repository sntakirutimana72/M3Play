__all__ = ('ilogging', )

__logger__ = None


def __setup__():
    from os import path, makedirs
    from datetime import datetime
    from utils.envs import res_dir
    from logging import basicConfig, DEBUG, getLogger

    global __logger__

    logfile_env = path.join(res_dir(), 'Logs')
    if not path.exists(logfile_env):
        try:
            makedirs(logfile_env)
        except:
            pass

    logfile_name = datetime.now().strftime('%B-%Y')
    basicConfig(filename=path.join(logfile_env, logfile_name + '.log'),
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
