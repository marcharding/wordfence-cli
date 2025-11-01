from ctypes import cdll, CDLL
from ctypes.util import find_library
from importlib import import_module
import os
import sys


class LibraryNotAvailableException(Exception):
    pass


def load_library(name: str) -> CDLL:

    # First, try system library search
    pathname = find_library(name)
    if pathname is not None:
        try:
            library = cdll.LoadLibrary(pathname)
            return library
        except OSError:
            pass

    # Fall back to PyInstaller bundle directory
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS

        # Search for library files matching common patterns
        import glob
        patterns = [
            f'lib{name}.so*',      # Linux: lib{name}.so, lib{name}.so.1, etc.
            f'lib{name}.dylib*',   # macOS: lib{name}.dylib
            f'{name}.dll',         # Windows: {name}.dll
        ]

        for pattern in patterns:
            matches = glob.glob(os.path.join(bundle_dir, pattern))
            for bundle_lib in sorted(matches):  # sorted for consistent ordering
                try:
                    library = cdll.LoadLibrary(bundle_lib)
                    return library
                except OSError:
                    continue

    raise LibraryNotAvailableException()


class OptionalUtility:

    def __init__(self, name):
        try:
            self.module = import_module('.' + name, 'wordfence.util')
        except LibraryNotAvailableException:
            self.module = None

    def is_available(self) -> bool:
        return self.module is not None
