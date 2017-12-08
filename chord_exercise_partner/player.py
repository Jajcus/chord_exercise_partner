# -*- coding: utf-8 -*-

"""Backing track player."""

import re
import threading
import time

from .exercise import LEAD_IN
from .midi import MIDDLE_C, note_off, note_on
from .tracks import LEAD_TRACK, MAIN_TRACKS, MIDI_INIT

# play notes that early or late, compensating for sleep time precision
ALLOW_EARLY = 0.001  # seconds
ALLOW_LATE = 0.020   # seconds

try:
    import rtmidi
except ImportError as err:
    rtmidi = None
    rtmidi_import_error = err # pylint: disable=invalid-name

# weights for sorting MIDI ports, to choose the optimal one
PORT_WEIGHTS = [
    (re.compile("^Midi Through"), 10),
    (re.compile(".*:qjackctl"), 20),
    ]

VIRT_PORT_NAME = "Chord Exercise Partner"

class MIDINotAvailable(Exception):
    """Raised when MIDI output is not available."""
    pass

class CompPlayer:
    """Backing track player.

    A MIDI sequencer, running in a separate thread for precise timing.
    """
    def __init__(self):
        self.exercise = None
        self.start_time = None    # wall clock start time
        self.p_start_time = None  # precise start time (probably meaningful
                                  # only in the player thread)
        self.quit = False
        self.port = None
        self.port_name = None
        self.available_ports = []
        self.thread = None
        self.track_name = None
        self.tempo = None
        self.update = False

        if not rtmidi:
            raise MIDINotAvailable("rtmidi module not available: {}"
                                   .format(rtmidi_import_error))

        try:
            midi, ports = self._get_available_ports()
        except rtmidi.RtMidiError as err:
            raise MIDINotAvailable("Could not find MIDI ports: {}".format(err))

        if ports:
            port_num = ports[0][0]
            print("Selected MIDI port:", ports[port_num])
            try:
                self.port = midi.open_port(port_num)
                self.port_name = ports[0][1]
            except rtmidi.RtMidiError as err:
                print("Could not open MIDI port: {}".format(err))

        if not self.port:
            print("Opening virtual midi port")
            try:
                self.port = midi.open_virtual_port(VIRT_PORT_NAME)
            except rtmidi.RtMidiError as err:
                raise MIDINotAvailable("Could not open virtual MIDI port: {}"
                                       .format(err))
            self.port_name = "<virtual>"

        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)
        self.thread = threading.Thread(name="comp player",
                                       daemon=True,
                                       target=self.run)
        self.thread.start()

    def __del__(self):
        """Clean up, stopping all sounds."""
        self.quit = True
        for _ in range(1000):
            if not self.thread:
                break
            time.sleep(0.01)
        if self.port:
            # all notes off
            for channel in range(0, 16):
                self.port.send_message([0xb0 + channel, 0x78, 0])
            self.port = None

    def _get_available_ports(self):
        """Return a MidiOut object and list of available ports.

        Ports are provided in (number, name) list, sorted by preference."""
        midi = rtmidi.MidiOut()
        ports = midi.get_ports()
        if not ports:
            self.available_ports = ["<virtual>"]

        print("MIDI out ports found:", ", ".join(ports))
        def _port_pref(item):
            name = item[1]
            for regexp, weight in PORT_WEIGHTS:
                if regexp.match(name):
                    return weight
            return 0
        sorted_ports = sorted(enumerate(ports), key=_port_pref)
        self.available_ports = [p[1] for p in sorted_ports] + ["<virtual>"]
        return midi, sorted_ports

    def change_port(self, port_name):
        """Attempt to change current MIDI output to the named port.

        Return True when the output is changed.
        """
        print("Change port request:", port_name)
        try:
            midi, ports = self._get_available_ports() # always refresh the list
        except rtmidi.RtMidiError as err:
            print("Could not list MIDI ports")
            return False
        if port_name == self.port_name:
            return False
        if port_name == "<virtual>":
            try:
                port = midi.open_virtual_port(VIRT_PORT_NAME)
            except rtmidi.RtMidiError as err:
                print("Could not open virtual port:", err)
                return False
        else:
            for num, name in ports:
                if name == port_name:
                    break
            else:
                print("Unknown MIDI port:", port_name)
                return False
            try:
                port = midi.open_port(num) # pylint: disable=undefined-loop-variable
            except rtmidi.RtMidiError as err:
                print("Could not open MIDI port:", err)
                return False

        self.port.close_port()
        self.port = port
        self.port_name = port_name

    def change_track(self, track_name):
        """Change current backing track."""
        with self.lock:
            self.track_name = track_name
            self.update = True
            self.cond.notify()

    def change_tempo(self, tempo, start_time=None):
        """Change current tempo and position."""
        with self.lock:
            self.tempo = tempo
            if start_time and self.start_time:
                self.p_start_time += start_time - self.start_time
                self.start_time = start_time
            self.update = True
            self.cond.notify()

    def prepare_track(self, pattern, bars=1, start=0):
        """Convert a backing track pattern to a list of timed MIDI events.

        Given number of bars will be generated, to be played from the start timestamp.
        """
        pattern_bars = len(pattern)
        events = []
        bar_d = self.exercise.bar_duration / self.tempo
        whn_d = self.exercise.whole_note_duration / self.tempo
        for bar in range(bars):
            song_bar = start + bar
            ex_bar = song_bar - LEAD_IN
            for bar_time, notes in pattern[bar % pattern_bars]:
                rel_time = (song_bar + bar_time) * bar_d
                on_time = self.p_start_time + rel_time
                for channel, note, velocity, duration in notes:
                    off_time = on_time + duration * whn_d
                    if note == "chord":
                        if ex_bar < 0 or ex_bar >= self.exercise.length:
                            continue
                        for chord_note in self.exercise.chord_notes(ex_bar):
                            note = MIDDLE_C + chord_note
                            events.append((on_time, note_on(channel, note, velocity)))
                            events.append((off_time, note_off(channel, note)))
                    else:
                        events.append((on_time, note_on(channel, note, velocity)))
                        events.append((off_time, note_off(channel, note)))
        return sorted(events)

    def start(self, exercise, main_track, tempo):
        """Start the player, return the exact start time."""
        with self.lock:
            self.exercise = exercise
            self.start_time = None
            self.track_name = main_track
            self.tempo = tempo
            self.update = True
            self.cond.notify()
            while not self.start_time:
                self.cond.wait()
        return self.start_time

    def run(self):
        """The main loop of the player."""
        try:
            with self.lock:
                while not self.quit:
                    while not self.exercise:
                        self.cond.wait(0.1)
                    self.start_time = time.time()
                    self.p_start_time = time.perf_counter()
                    self.cond.notify()
                    events = []
                    while not self.quit and self.start_time and self.exercise:
                        if self.update:
                            for message in MIDI_INIT:
                                self.port.send_message(message)
                            events = self.prepare_track(LEAD_TRACK,
                                                        LEAD_IN)
                            track = MAIN_TRACKS[self.track_name]
                            events += self.prepare_track(track,
                                                         self.exercise.length,
                                                         LEAD_IN)
                            self.update = False
                        ev_time, message = events[0]
                        now = time.perf_counter()
                        lag = now - ev_time
                        if lag > -ALLOW_EARLY:
                            events = events[1:]
                            if lag < ALLOW_LATE and self.port:
                                self.port.send_message(message)
                            if not events:
                                break
                            ev_time = events[0][0]
                            now = time.perf_counter() # send_message() could eat some
                        if ev_time > now:
                            self.cond.wait(ev_time - now)
                    self.start_time = None
                    self.exercise = None
                    self.cond.notify()
        finally:
            self.thread = None

    def stop(self):
        """Stop playing current exercise track."""
        with self.lock:
            self.exercise = None
            self.cond.notify()
