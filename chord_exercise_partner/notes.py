#!/usr/bin/python3

"""
Basic music theory – note names, scale harmonisation.
"""
         # 0    1     2    3    4     5    6     7    8    9    10    11
S_NOTES = ("A", "A♯", "B", "C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯")
F_NOTES = ("A", "B♭", "B", "C", "D♭", "D", "E♭", "E", "F", "G♭", "G", "A♭")
FLATS =   (0,   1,    0,   0,   1,    0,   1,    0,   1,   0,    0,    1)
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
    chord_note, chord_quality = HARMONISATION[degree]
    chord_root = (root + chord_note) % 12
    chord_name = NOTES[FLATS[root]][chord_root]
    return chord_name +  chord_quality
