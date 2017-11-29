# -*- coding: utf-8 -*-

"""Midi messages."""

def note_on(channel, note, velocity):
    """Create a 'note on' midi message.

    Channel should be 1-16, note: 0-127 and velocity 0.0-1.0."""
    return [0x90 + (channel - 1) % 16, note % 128, int(velocity * 127) % 128]

def note_off(channel, note, velocity=0.0):
    """Create a 'note off' midi message.

    Channel should be 1-16, note: 0-127 and velocity 0.0-1.0."""
    return [0x80 + (channel - 1) % 16, note % 128, int(velocity * 127) % 128]

def program_change(channel, program):
    """Create a 'program change' midi message.

    Channel should be:  1-16, program: 1-128."""
    return [0xc0 + (channel - 1) % 16, (program - 1) % 128]

MIDDLE_C = 60
