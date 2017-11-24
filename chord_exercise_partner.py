#!/usr/bin/python3

import random
import re
import threading
import time

import tkinter as tk

LEAD_IN = 2 # bars
EXERCISE_LENGTH = 10 # bars
TEMPO = 60 # BPM
CHORD_NAME_DELAY = 2 # beats

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

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]

SCALE_LABEL_FONT = ("serif", -26)
BAR_LABEL_FONT = ("serif", -20)

CANVAS_HEIGHT = 50
CANVAS_WIDTH = 800
CANVAS_FONT = "{sans -10}"

ARROW_LENGTH = CANVAS_HEIGHT * 0.375
ARROW_HEAD_WIDTH = 5
ARROW_HEAD_LENGTH = 7

BAR_HEIGHT = 40
BEAT_RADIUS = 5
SMALL_BEAT_RADIUS = 2

BAR_LENGTH = 200

BEAT_OFFSET = 50

BEAT_LENGTH = BAR_LENGTH / 4
BAR_OFFSET = BEAT_OFFSET - BEAT_LENGTH / 2

D_BASS = 35
D_STICK = 37
D_SNARE = 38
D_HH_CLOSED = 42

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

def scale_name(root):
    flats = FLATS[root]
    return "{}-major".format(NOTES[flats][root])

def chord_name(root, degree):
    chord_note, chord_quality = HARMONISATION[degree]
    chord_root = (root + chord_note) % 12
    chord_name = NOTES[FLATS[root]][chord_root]
    return chord_name +  chord_quality

class MIDINotAvailable(Exception):
    pass

class CompPlayer:
    _PORT_WEIGHTS = [
            (re.compile("^Midi Through"), 10),
            (re.compile(".*:qjackctl"), 20),
            ]
    _VIRT_PORT_NAME = "Chord Exercise Partner"
    def __init__(self):
        self.exercise = None
        self.start_time = None
        self.quit = False
        self.port = None
        self.port_name = None
        self.available_ports = []
        self.thread = None
        self.track_name = None

        try:
            import rtmidi
        except ImportError as err:
            raise MIDINotAvailable("rtmidi module not available: {}".format(err))

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
                self.port = midi.open_virtual_port(self._VIRT_PORT_NAME)
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
        self.quit = True
        for i in range(1000):
            if not self.thread:
                break
            time.sleep(0.01)
        if self.port:
            # all notes off
            for ch in range(0, 16):
                self.port.send_message([0xb0 + ch, 0x78, 0])
            self.port = None

    def _get_available_ports(self):
        import rtmidi
        midi = rtmidi.MidiOut()
        ports = midi.get_ports()
        if not ports:
            self.available_ports = ["<virtual>"]

        print("MIDI out ports found:", ", ".join(ports))
        def _port_pref(item):
            num, name = item
            for re, weight in self._PORT_WEIGHTS:
                if re.match(name):
                    return weight
            else:
                return 0
        sorted_ports = sorted(enumerate(ports), key=_port_pref)
        self.available_ports = [p[1] for p in sorted_ports] + ["<virtual>"]
        return midi, sorted_ports

    def change_port(self, port_name):
        print("Change port request:", port_name)
        import rtmidi
        try:
            midi, ports = self._get_available_ports() # always refresh the list
        except rtmidi.RtMidiError as err:
            print("Could not list MIDI ports")
            return False
        if port_name == self.port_name:
            return False
        if port_name == "<virtual>":
            try:
                port = midi.open_virtual_port(self._VIRT_PORT_NAME)
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
                port = midi.open_port(num)
            except rtmidi.RtMidiError as err:
                print("Could not open MIDI port:", err)
                return False

        self.port.close_port()
        self.port = port
        self.port_name = port_name

    def prepare_track(self, pattern, bars=1, start=0):
        pattern_bars = len(pattern)
        events = []
        for bar in range(bars):
            for bar_time, notes in pattern[bar % pattern_bars]:
                rel_time = (start + bar + bar_time) * 60.0 * 4.0 / TEMPO
                on_time = self.start_time + rel_time
                for channel, note, velocity, duration in notes:
                    off_time = on_time + duration * 60.0 * 4.0 / TEMPO
                    message = [0x90 + (channel - 1) % 16,
                               note % 128,
                               int(velocity * 127) % 128]
                    events.append((on_time, message))
                    message = [0x80 + (channel - 1) % 16,
                               note % 128,
                               int(velocity * 127) % 128]
                    events.append((off_time, message))
        return sorted(events)

    def start(self, exercise, main_track):
        """Start the player, return the start time."""
        with self.lock:
            self.exercise = exercise
            self.start_time = None
            self.track_name = main_track
            self.cond.notify()
            while not self.start_time:
                self.cond.wait()
        return self.start_time

    def run(self):
        try:
            with self.lock:
                while not self.quit:
                    while not self.exercise:
                        self.cond.wait(0.1)
                    self.start_time = time.time()
                    self.cond.notify()
                    events = self.prepare_track(LEAD_TRACK, LEAD_IN)
                    events += self.prepare_track(self.track_name, EXERCISE_LENGTH, LEAD_IN)
                    while not self.quit and self.start_time and self.exercise and events:
                        ev_time, message = events[0]
                        now = time.time()
                        if ev_time <= now:
                            events = events[1:]
                            if self.port:
                                self.port.send_message(message)
                            if not events:
                                break
                            ev_time = events[0][0]
                            now = time.time() # send_message() could eat some
                        if ev_time > now:
                            self.cond.wait(ev_time - now)
                    self.start_time = None
                    self.exercise = None
                    self.cond.notify()
        finally:
            self.thread = None

    def stop(self):
        with self.lock:
            self.exercise = None
            self.cond.notify()

class Exercise:
    def __init__(self):
        random.seed()
        self.root = random.randint(0, 11)
        self.scale_name = scale_name(self.root)

        print("The scale is:", self.scale_name)

        self.progression = [random.randint(0, 6)
                            for i in range(EXERCISE_LENGTH)]

        print("The progression is: {}".format(",".join(ROMAN[x]
                                                for x in self.progression)))
        self.chord_names = [chord_name(self.root, x) for x in self.progression]
        #print("Which is: {}".format(",".join(self.chord_names)))

class CEP_App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.start_time = None
        self.end_time = None
        self.bar = None
        self.beat = None
        self.exercise = None

        self.track_v = None
        self.midi_port_v = None

        try:
            self.player = CompPlayer()
        except MIDINotAvailable as err:
            print("MIDI player not available")
            self.player = None

        self.pack(expand=1, fill=tk.BOTH)
        self.create_widgets()
        self.draw_markers()

        self.new_exercise()

    def create_widgets(self):
        self.scale_l = tk.Label(self, font=SCALE_LABEL_FONT)
        self.scale_l.pack(side=tk.TOP)

        self.chord_d_l = tk.Label(self, font=BAR_LABEL_FONT)
        self.chord_d_l.pack()

        self.chord_n_l = tk.Label(self, font=BAR_LABEL_FONT)
        self.chord_n_l.pack()

        self.canvases_f = tk.Frame(self, padx=0, pady=0)
        self.top_canvas = tk.Canvas(self.canvases_f,
                                height=CANVAS_HEIGHT / 2,
                                width=CANVAS_WIDTH,
                                bd=0, highlightthickness=0, relief='ridge',
                                bg="white")
        self.top_canvas.pack(fill=tk.X, expand=1, pady=0, ipady=0)

        self.canvas = tk.Canvas(self.canvases_f,
                                height=CANVAS_HEIGHT,
                                width=CANVAS_WIDTH,
                                bd=0, highlightthickness=0, relief='ridge',
                                bg="white")
        self.canvas.pack(fill=tk.X, expand=1)

        self.bottom_canvas = tk.Canvas(self.canvases_f,
                                height=CANVAS_HEIGHT / 2,
                                width=CANVAS_WIDTH,
                                bd=0, highlightthickness=0, relief='ridge',
                                bg="white")
        self.bottom_canvas.pack(fill=tk.X, expand=1, pady=0, ipady=0)

        self.canvases_f.pack(fill=tk.X, expand=1, pady=0, ipady=0)

        self.settings_f = tk.Frame(self)
        self.settings_f.pack()

        self.buttons_f = tk.Frame(self)
        self.buttons_f.pack(side=tk.BOTTOM)

        self.start_b = tk.Button(self.buttons_f)
        self.start_b["text"] = "Start"
        self.start_b["command"] = self.start
        self.start_b["state"] = tk.NORMAL
        self.start_b.pack(side=tk.LEFT, padx=5, pady=5)

        self.new_b = tk.Button(self.buttons_f)
        self.new_b["text"] = "New Exercise"
        self.new_b["command"] = self.new_exercise
        self.new_b.pack(side=tk.LEFT, padx=5, pady=5)

        self.quit_b = tk.Button(self.buttons_f)
        self.quit_b["text"] = "Quit"
        self.quit_b["command"] = self.master.destroy
        self.quit_b.pack(side=tk.LEFT, padx=5, pady=5)

        self.update_settings_widgets()

    def update_settings_widgets(self):
        for widget in self.settings_f.winfo_children():
            widget.destroy()

        if self.player:
            label = tk.Label(self.settings_f, text="Backing track:")
            label.pack(side=tk.LEFT)

            if not self.track_v:
                self.track_v = tk.StringVar(self.settings_f)
                self.track_v.set(DEFAULT_TRACK)

            track_names = list(MAIN_TRACKS)
            self.track_o = tk.OptionMenu(self.settings_f,
                                         self.track_v,
                                         *track_names)
            self.track_o.pack(side=tk.LEFT)

            label = tk.Label(self.settings_f, text="MIDI port:")
            label.pack(side=tk.LEFT)

            if not self.midi_port_v:
                self.midi_port_v = tk.StringVar(self.settings_f)
                self.midi_port_v.set(self.player.port_name)
                self.midi_port_v.trace("w", self.midi_port_changed)
            else:
                self.midi_port_v.set(self.player.port_name)

            self.midi_port_o = tk.OptionMenu(self.settings_f,
                                             self.midi_port_v,
                                             *self.player.available_ports)
            self.midi_port_o.pack(side=tk.LEFT)


    def midi_port_changed(self, *args):
        if self.player:
            self.player.change_port(self.midi_port_v.get())
        self.update_settings_widgets()

    def draw_canvas(self):

        self.canvas.delete(tk.ALL)

        y_padding = (CANVAS_HEIGHT - BAR_HEIGHT) / 2

        # bars
        y = y_padding
        for i in range(LEAD_IN + EXERCISE_LENGTH + 1):
            x = BAR_OFFSET + i * BAR_LENGTH
            self.canvas.create_line(x, y, x, y + BAR_HEIGHT, fill="black")

        # lead-in beats
        y = CANVAS_HEIGHT - y_padding - BEAT_RADIUS
        for i in range(LEAD_IN):
            for j in range(4):
                x = BEAT_OFFSET + i * BAR_LENGTH + j * BEAT_LENGTH
                self.canvas.create_oval(x - SMALL_BEAT_RADIUS,
                                        y - SMALL_BEAT_RADIUS,
                                        x + SMALL_BEAT_RADIUS,
                                        y + SMALL_BEAT_RADIUS,
                                        fill="black")

        # exercise beats and chord numbers
        for i in range(EXERCISE_LENGTH):
            for j in range(4):
                x = BEAT_OFFSET + (LEAD_IN + i) * BAR_LENGTH + j * BEAT_LENGTH
                self.canvas.create_oval(x - BEAT_RADIUS,
                                        y - BEAT_RADIUS,
                                        x + BEAT_RADIUS,
                                        y + BEAT_RADIUS,
                                        fill="black")
            x = BEAT_OFFSET + (LEAD_IN + i) * BAR_LENGTH - BEAT_RADIUS
            self.canvas.create_text(x, y_padding,
                                    anchor=tk.NW,
                                    text=ROMAN[self.exercise.progression[i]],
                                    fill="black",
                                    font=CANVAS_FONT)

        x, y, width, height = self.canvas.bbox(tk.ALL)
        self.canvas_length = width + 4096 # to be longer than any screen width

        self.canvas.config(scrollregion=(0, y, self.canvas_length, height),
                           xscrollincrement='1')

    def draw_markers(self):

        # position markers
        x0 = BEAT_OFFSET
        x1 = x0 - ARROW_HEAD_WIDTH
        x2 = x0 + ARROW_HEAD_WIDTH
        y0 = 0
        y1 = y0 + ARROW_LENGTH
        y2 = y0 + ARROW_HEAD_LENGTH

        h = CANVAS_HEIGHT / 2

        self.bottom_canvas.create_line(x0, y0, x0, y1)
        self.bottom_canvas.create_line(x0, y0, x1, y2)
        self.bottom_canvas.create_line(x0, y0, x2, y2)
        self.top_canvas.create_line(x0, h - y0, x0, h - y1)
        self.top_canvas.create_line(x0, h - y0, x1, h - y2)
        self.top_canvas.create_line(x0, h - y0, x2, h - y2)

    def start(self):
        if self.player:
            self.player.stop()

        self.start_b["text"] = "Restart"
        self.chord_d_l["text"] = "Current chord degree: –"
        self.chord_n_l["text"] = "Current chord name: –"

        self.canvas.xview_moveto(0)

        song_length = ((LEAD_IN + EXERCISE_LENGTH) * 4.0) * 60 / TEMPO
        print("Song length: {}s".format(song_length))

        if self.player:
            track = MAIN_TRACKS[self.track_v.get()]
            self.start_time = self.player.start(self.exercise, track)
        else:
            self.start_time = time.time()

        self.end_time = self.start_time + song_length
        self.progress()

    def progress(self):
        if not self.start_time:
            # exercise stopped
            return

        now = time.time()
        total_bars = LEAD_IN + EXERCISE_LENGTH
        pos = now - self.start_time

        if pos < 0:
            print("Time runs backwards?!")
            return

        beat_pos = pos * TEMPO / 60
        bar = int(beat_pos // 4)
        beat = beat_pos % 4
        hours = int(pos / 3600)
        minutes = int((pos % 3600) / 60)
        seconds = int(pos % 60)

        if bar != self.bar and bar < total_bars:
            self.bar = bar
            if bar >= LEAD_IN:
                chord_degree = self.exercise.progression[bar - LEAD_IN] + 1
                self.chord_d_l["text"] = "Current chord degree: {}".format(chord_degree)
                self.chord_n_l["text"] = "Current chord name: ?"

        if beat != self.beat and bar < total_bars:
            self.beat = beat
            if bar >= LEAD_IN and beat >= CHORD_NAME_DELAY:
                chord_name = self.exercise.chord_names[bar - LEAD_IN]
                self.chord_n_l["text"] = "Current chord name: " + chord_name


        canvas_target = int(bar * BAR_LENGTH + beat * BEAT_LENGTH)
        canvas_x = int(self.canvas.canvasx(0))

        if canvas_target > canvas_x:
            self.canvas.xview_scroll(canvas_target - canvas_x, tk.UNITS)
        if now < self.end_time:
            self.canvas.after(10, self.progress)

    def new_exercise(self):
        if self.player:
            self.player.stop()
        self.exercise = Exercise()
        self.start_time = None
        self.end_time = None
        self.bar = None
        self.beat = None
        self.canvas.xview_moveto(0)
        self.chord_d_l["text"] = "Current chord degree: –"
        self.chord_n_l["text"] = "Current chord name: –"
        self.scale_l["text"] = "The scale is: {}".format(self.exercise.scale_name)
        self.draw_canvas()
        self.start_b["text"] = "Start"

root_w = tk.Tk()
root_w.title("Chord Exercise Partner")
app = CEP_App(master=root_w)
app.mainloop()

