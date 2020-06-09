__all__ = (
    'stringedArray_2_array',  'get_metadata',
    'format_timeframe', 'write_cache', 'read_cache'
)

import json
from pathlib import Path
from tinytag import TinyTag


def stringedArray_2_array(s_array: str, parser=float):
    """ This function converts a stringed-like array or list of numbers into a real type list.

        ..A stringed-like list to be converted must look like `[.1, 1]`
    """
    return (parser(digit) for digit in s_array.strip(' [] ').split(','))


def get_metadata(source: Path):
    """ Access media metadata and return some like album, artist, duration, ... """
    metadata = TinyTag.get(source)

    return {
        'name': source.stem,
        'Genre': metadata.genre,
        'Album': metadata.album,
        'Artist': metadata.artist,
        'suffix': source.suffix[1:],
    }, metadata.duration


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
