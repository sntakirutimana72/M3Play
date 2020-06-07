if __name__ == '__main__':
    from utils.loggers import ilogging
    from protocols import routine_001

    # Log in when the application was first invoked
    ilogging('SYAI-M3Play started..', 'i')
    # Protocol - 001 execution
    routine_001()

    from uix.app import M3PlayApp
    from utils.helpers import cli_argv

    M3PlayApp(*cli_argv()).run()

    # Log in when the application was terminated.
    ilogging('SYAI-M3Play terminated..', 'i')
