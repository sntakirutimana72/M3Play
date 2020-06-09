__all__ = ('cli_argv', )

import sys
from simulations import generate_cli_args


def cli_argv():
    """ Read Command-Line arguments and remove default ones and return the rests """
    return generate_cli_args()  # sys.argv[1:]
