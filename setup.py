from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(
    packages=[],
    excludes=[],
    append_script_to_exe=True,
    include_msvcr=True,
)

import sys
base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('mcgen.py', base=base)
]

setup(name='Chargen',
      version='0.1',
      description='A chargen for Mindy',
      options=dict(build_exe=buildOptions),
      executables=executables)
