# -*- coding: utf-8 -*-

"""
Basic music theory – note names, scale harmonisation.
"""

# pylint: disable=bad-whitespace,

         # 0    1     2    3    4     5    6     7    8    9    10    11
S_NOTES = ("C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B")
F_NOTES = ("C", "D♭", "D", "E♭", "E", "F", "G♭", "G", "A♭", "A", "B♭", "B")
FLATS =   (0,   1,    0,   1,    0,   1,   0,    0,   1,    0,   1,    0)

NOTES = (S_NOTES, F_NOTES)

NOTE_NUMBERS = {name: i for i, name in list(enumerate(S_NOTES)) + list(enumerate(F_NOTES))}

SCALES = {
    "major": ["C", "G", "D", "A", "E", "B", "F♯", "D♭", "A♭", "E♭", "B♭", "F"],
    "minor": ["A", "E", "B", "F♯", "C♯", "G♯", "D♯", "B♭", "F", "C", "G", "D"],
}

HARMONIZATION = {
    "triads": {
        "major": [
            (0, ""),     # major chord on root
            (2, "m"),    # minor chord on major second
            (4, "m"),    # minor chord on major third
            (5, ""),     # major chord on perfect fourth
            (7, ("", "7")),     # major or 7th chord on perfect fifth
            (9, "m"),    # minor chord on major sixth
            (11, "dim"), # diminished chord on major seventh
            ],
        "minor": [
            (0, "m"),        # minor chord on root
            (2, "dim"),      # diminished chord on major second
            (3, ""),         # major chord on minor third
            (5, "m"),        # minor chord on perfect fourth
            (7, ("m", "")),  # minor or major chord on perfect fifth
            (8, ""),         # major chord on minor sixth
            (10, ("", "7")), # major or seventh chord on minor seventh
            ],
    },
    "7ths": {
        "major": [
            (0, "maj7"),  # major 7th chord on root
            (2, "m7"),    # minor 7th chord on major second
            (4, "m7"),    # minor 7th chord on major third
            (5, "maj7"),  # major 7th chord on perfect fourth
            (7, "7"),     # 7th chord on perfect fifth
            (9, "m7"),    # minor 7th chord on major sixth
            (11, "m7♭5"), # half-diminished chord on major seventh
            ],
        "minor": [
            (0, "m7"),    # minor chord on root
            (2, "m7♭5"),  # diminished chord on major second
            (3, "maj7"),  # major chord on minor third
            (5, "m7"),    # minor chord on perfect fourth
            (7, "m7"),    # minor or major chord on perfect fifth
            (8, "maj7"),  # major chord on minor sixth
            (10, "7"),    # major or seventh chord on minor seventh
            ],
    },
    }

def note_name(note):
    """Convert note (pitch class) number to a note name."""
    flats = FLATS[note]
    return NOTES[flats][note]

def note_number(name):
    """Convert note name to a number."""
    return NOTE_NUMBERS[name]

def normalize_scale_root(note, mode):
    """Convert arbitrary note name or number to the one used to name scale."""
    if note in SCALES[mode]:
        return note
    if isinstance(note, str):
        note = NOTE_NUMBERS[note]
    name = F_NOTES[note]
    if "♭" not in name or name in SCALES[mode]:
        return name
    return S_NOTES[note]

def chord_name(root, degree, mode, harmonisation="triads"):
    """Return name of a chord build on given degree of a root-mode scale."""
    if isinstance(root, int):
        root_note = root
        root = normalize_scale_root(root, mode)
    else:
        root_note = NOTE_NUMBERS[root]

    # from circle of fifths
    use_flats = SCALES[mode].index(root) > 5

    note, quality = HARMONIZATION[harmonisation][mode][degree]

    chord_root = (root_note + note) % 12
    name = NOTES[use_flats][chord_root]

    if not isinstance(quality, str):
        return " or ".join((name + q) for q in quality)
    return name + quality
