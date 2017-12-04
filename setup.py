#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from setuptools import setup

extra = {}
if "build_exe" in sys.argv:
    try:
        from cx_Freeze import setup, Executable
        base = None
        if sys.platform == "win32":
                base = "Win32GUI"
        extra["executables"] = [Executable("chord_exercise_partner.py", base=base)]
    except ImportError:
        pass

if sys.platform == 'darwin':
    extra["setup_requires"] = ['py2app']
    extra["app"] = ["chord_exercise_partner.py"]
    plist = {
            "CFBundleIdentifier": "net.jajcus.chord_exercise_partner",
            "CFBundleName": "Chord Exercise Partner",
            "CFBundleDisplayName": "Chord Exercise Partner",
            }
    extra["options"] = {"py2app": {"plist": plist}}

setup(
    name="jajcus.chord_exercise_partner",
    version="0.6",
    packages=["jajcus.chord_exercise_partner"],
    package_dir={'jajcus': ''},
    entry_points={
        'gui_scripts': [
            "chord_exercise_partner = jajcus.chord_exercise_partner.ui:main",
        ]
    },
    python_requires=">=3.4",
    extras_require={
        'MIDI':  ["python-rtmidi"],
    },
    zip_safe=False, # ZIP install breaks namespace handling
    **extra
)

