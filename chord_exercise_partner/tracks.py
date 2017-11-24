#!/usr/bin/python3

# General MIDI drum note numbers
D_BASS = 35
D_STICK = 37
D_SNARE = 38
D_HH_CLOSED = 42

# General MIDI drums channel
CH_DRUMS = 10

#   [(time_in_bar, [(channel, note, velocity, duration), ...]),...]
LEAD_TRACK = [
    # bar 1
    [
    (0.0  , [(CH_DRUMS, D_STICK, 0.5, 0.5)]),
    (0.5  , [(CH_DRUMS, D_STICK, 0.5, 0.5)]),
    ],
    # bar 2
    [
    (0.0  , [(CH_DRUMS, D_STICK, 0.5, 0.25)]),
    (0.25 , [(CH_DRUMS, D_STICK, 0.5, 0.25)]),
    (0.5  , [(CH_DRUMS, D_STICK, 0.5, 0.25)]),
    (0.75 , [(CH_DRUMS, D_STICK, 0.5, 0.25)]),
    ],
]

MAIN_TRACKS = {
        "straight" : [
    # single bar
    [
    (0.0  , [(CH_DRUMS, D_BASS, 0.5, 0.5), (CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.125, [(CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.25 , [(CH_DRUMS, D_SNARE, 0.5, 0.25), (CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.375, [(CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.5  , [(CH_DRUMS, D_BASS, 0.5, 0.5), (CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.625, [(CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.75 , [(CH_DRUMS, D_SNARE, 0.5, 0.25), (CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.875, [(CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    ]
    ],
        "swing" : [
    [
    (0.0  , [(CH_DRUMS, D_BASS, 0.5, 0.5), (CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.167, [(CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.25 , [(CH_DRUMS, D_SNARE, 0.5, 0.25), (CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.417, [(CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.5  , [(CH_DRUMS, D_BASS, 0.5, 0.5), (CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.667, [(CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.75 , [(CH_DRUMS, D_SNARE, 0.5, 0.25), (CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    (0.917, [(CH_DRUMS, D_HH_CLOSED, 0.5, 0.125)]),
    ]
    ]}

DEFAULT_TRACK = "straight"
