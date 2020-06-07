__all__ = (
    'stringedArray_2_array',  # 'get_metadata',
    'format_timeframe', 'write_cache', 'read_cache'
)

import json


def stringedArray_2_array(stringed: str, converter=float):
    """ This function converts a stringed-like array or list of numbers into a real type list.

        ..A stringed-like list to be converted must look like `[.1, 1]`
    """
    return [converter(digit) for digit in stringed.strip(' [] ').split(',')]


def get_metadata(source: str) -> dict:
    from tinytag import TinyTag
    return TinyTag.get(source).as_dict()


def format_timeframe(timeframe: float):
    """ Formats the timestamp provided to look like a count-down timer """

    stamp_hours = timeframe // 3600
    stamp_minutes = (timeframe % 3600) // 60
    stamp_seconds = (timeframe % 3600) % 60

    if not stamp_hours:
        formatted_stamp = f'{stamp_minutes:02.0f}:{stamp_seconds:02.0f}'
    else:
        formatted_stamp = f'{stamp_hours:.0f}:{stamp_minutes:02.0f}:{stamp_seconds:02.0f}'

    return formatted_stamp


def write_cache(data):
    pass


def read_cache():
    pass
