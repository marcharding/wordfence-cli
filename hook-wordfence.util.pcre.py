"""
PyInstaller hook for wordfence.util.pcre module.
This hook ensures that libpcre is included in the statically build bundle.
"""
from ctypes.util import find_library
import os
import subprocess

binaries = []

# Find the libpcre library
pcre_path = find_library('pcre')

if pcre_path:
    # If find_library returns just a name, resolve it to full path
    if not os.path.isabs(pcre_path):
        # Try to find the full path to libpcre.so using ldconfig
        try:
            result = subprocess.run(
                ['/sbin/ldconfig', '-p'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'libpcre.so' in line and '=>' in line:
                        full_path = line.split('=>')[1].strip()
                        if os.path.exists(full_path):
                            pcre_path = full_path
                            break
        except (FileNotFoundError, Exception):
            print("\033[91mWARNING: PyInstaller hook: no libpcre found\033[0m")

    # Add the library as a binary
    if pcre_path and os.path.isabs(pcre_path) and os.path.exists(pcre_path):
        binaries = [(pcre_path, '.')]
        print(f"PyInstaller hook: Including libpcre from {pcre_path}")

# Ensure all submodules are included
hiddenimports = [
    'wordfence.util.pcre.pcre',
    'wordfence.util.pcre.bindings',
]
