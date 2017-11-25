#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="jajcus.chord_exercise_partner",
    version="0.1",
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
)

