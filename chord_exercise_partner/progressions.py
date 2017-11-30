"""Built-in chord progressions."""

from itertools import cycle, islice

PROGRESSIONS = {
        "12 bar blues": [0, 0, 0, 0, 3, 3, 0, 0, 4, 3, 0, 0],
        "circle": [0, 3, 6, 2, 5, 1, 4, 0],
        "scale": [0, 1, 2, 3, 4, 5, 6, 0],
        "I-V": [0, 4],
        "I-IV": [0, 3],
        }

def get_progressions():
    """Return names of available progressions."""
    return list(PROGRESSIONS)

def progression_length(name, suggested_len, max_len):
    """Get possible lenghs of exercises based on the named progression.

    Return (current_length, available_lengths) tuple."""
    progression = PROGRESSIONS[name]
    base_len = len(progression)
    options = range(base_len, max_len + 1, base_len)
    if not options:
        options = [base_len]
    if suggested_len < base_len:
        return base_len, options
    repeats = round(float(suggested_len) / base_len)
    return base_len * repeats, options

def get_progression(name, length):
    progression = PROGRESSIONS[name]
    return list(islice(cycle(progression), length))
