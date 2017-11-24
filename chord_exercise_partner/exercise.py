#!/usr/bin/python3

"""C.E.P. exercise generator."""

import random

from .notes import chord_name, scale_name

LEAD_IN = 2 # bars
EXERCISE_LENGTH = 10 # bars
TEMPO = 60 # BPM

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]

class Exercise:
    """An exercise – a scale and chord progression to play."""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        random.seed()
        self.root = random.randint(0, 11)
        self.scale_name = scale_name(self.root)

        print("The scale is:", self.scale_name)

        self.progression = [random.randint(0, 6)
                            for i in range(EXERCISE_LENGTH)]

        roman_numbers = [ROMAN[x] for x in self.progression]
        print("The progression is: {}".format(",".join(roman_numbers)))
        self.chord_names = [chord_name(self.root, x) for x in self.progression]
        #print("Which is: {}".format(",".join(self.chord_names)))
