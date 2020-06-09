import re
from utils.cfg import cfg_getter


def is_format_allowed(file_object: object) -> bool:
    """ This function verifies dropped or imported file extension against allowed formats """

    is_allowed = re.compile(
        f".({cfg_getter('MODULAR', 'formats').strip().replace(', ', '|')})", re.I
    ).search(file_object.suffix)

    return True if is_allowed is not None else is_allowed


