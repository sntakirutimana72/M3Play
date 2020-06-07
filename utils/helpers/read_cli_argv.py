__all__ = ('cli_argv', )

import sys


def cli_argv():
    """ Read Command-Line arguments and remove default ones and return the rests """
    return sys.argv[1:]
