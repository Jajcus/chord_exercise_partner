#!/usr/bin/python3

"""
Basic music theory – note names, scale harmonisation.
"""

# pylint: disable=bad-whitespace,

         # 0    1     2    3    4     5    6     7    8    9    10    11
S_NOTES = ("C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B")
F_NOTES = ("C", "D♭", "D", "E♭", "E", "F", "G♭", "G", "A♭", "A", "B♭", "B")
FLATS =   (0,   1,    0,   1,    0,   1,   0,    0,   1,    0,   1,    0)
NOTES = (S_NOTES, F_NOTES)

# Major scale
HARMONISATION = [
    (0, ""),     # major chord on root
    (2, "m"),    # minor chord on major second
    (4, "m"),    # minor chord on major third
    (5, ""),     # major chord on perfect fourth
    (7, "7"),    # 7th chord on perfect fifth
    (9, "m"),    # minor chord on major sixth
    (11, "dim"), # diminished chord on major seventh
    ]

def scale_name(root):
    """Convert root note (pitch class) number to a major scale name."""
    flats = FLATS[root]
    return "{}-major".format(NOTES[flats][root])

def chord_name(root, degree):
    """Return name of a chord build on given degree of a root-major scale."""
    note, quality = HARMONISATION[degree]
    root = (root + note) % 12
    name = NOTES[FLATS[root]][root]
    return name + quality
