__all__ = ('generate_cli_args', )

from pathlib import Path


def generate_cli_args():
    return (str(audio_file) for audio_file in Path('/media/nuru/SYAI/old-os-data/Music/massage').glob('*.*'))
