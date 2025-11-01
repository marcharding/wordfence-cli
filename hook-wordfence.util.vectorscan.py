"""
PyInstaller hook for wordfence.util.vectorscan module.
This hook ensures that libhs (vectorscan) is included in the statically build bundle.
"""
from ctypes.util import find_library
import os
import subprocess

binaries = []

# Find the libhs library (vectorscan/hyperscan)
hs_path = find_library('hs')

if hs_path:
    # If find_library returns just a name, resolve it to full path
    if not os.path.isabs(hs_path):
        # Try to find the full path to libhs.so using ldconfig
        try:
            result = subprocess.run(
                ['/sbin/ldconfig', '-p'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'libhs.so' in line and '=>' in line:
                        full_path = line.split('=>')[1].strip()
                        if os.path.exists(full_path):
                            hs_path = full_path
                            break
        except (FileNotFoundError, Exception):
            print("\033[91mWARNING: PyInstaller hook: no libhs (vectorscan) found\033[0m")

    # Add the library as a binary
    if hs_path and os.path.isabs(hs_path) and os.path.exists(hs_path):
        binaries = [(hs_path, '.')]
        print(f"PyInstaller hook: Including libhs (vectorscan) from {hs_path}")

# Ensure all submodules are included
hiddenimports = [
    'wordfence.util.vectorscan.vectorscan',
    'wordfence.util.vectorscan.bindings',
]
