if __name__ == '__main__':
    from utils.loggers import ilogging
    from protocols import routine_001

    ilogging('SYAI-M3Play started..', 'i')
    routine_001()

    from uix.app import M3PlayApp
    from utils.helpers import cli_argv

    M3PlayApp(*cli_argv()).run()

    ilogging('SYAI-M3Play terminated..', 'i')
