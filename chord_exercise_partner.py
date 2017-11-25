#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

if sys.version_info < (3, 4):
    print("Python >= 3.4 required!")
    sys.exit(1)

from chord_exercise_partner import ui

if __name__ == "__main__":
    ui.main()
