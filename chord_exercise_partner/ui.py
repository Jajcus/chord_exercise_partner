# -*- coding: utf-8 -*-

"""C.E.P. UI implementation."""

import time
import tkinter as tk

from .exercise import DEFAULT_LENGTH, LEAD_IN, Exercise
from .notes import HARMONIZATION, SCALES, normalize_scale_root
from .player import CompPlayer, MIDINotAvailable
from .progressions import get_progression, get_progressions, progression_length
from .timing import check_sleep_precision, check_time_resolution
from .tracks import DEFAULT_TRACK, MAIN_TRACKS

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]

SCALE_LABEL_FONT = ("serif", -24)
SCALE_NAME_FONT = ("serif", -26)

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

CHORD_NAME_DELAY = 2 # beats

MIN_TEMPO = 20
MAX_TEMPO = 200
DEFAULT_TEMPO = 60

class CEPApplication(tk.Frame):
    """Application window."""
    # pylint: disable=too-many-ancestors,too-many-instance-attributes
    def __init__(self, master=None):
        super().__init__(master)
        self.start_time = None
        self.end_time = None
        self.bar = None
        self.beat = None
        self.exercise = None
        self.tempo = DEFAULT_TEMPO
        self.paused_at = None

        self.tempo_s = None
        self.scale_root_v = None
        self.scale_root_o = None
        self.scale_mode_v = None
        self.scale_mode_o = None
        self.harmonization_v = None
        self.harmonization_o = None
        self.length_v = None
        self.length_o = None
        self.progression_v = None
        self.progression_o = None

        self.track_v = None
        self.track_o = None
        self.midi_port_v = None
        self.midi_port_o = None
        self.latency_s = None

        try:
            self.player = CompPlayer()
        except MIDINotAvailable as err:
            print("MIDI player not available:", err)
            self.player = None

        self.pack(expand=1, fill=tk.BOTH)
        self.create_widgets()
        self.draw_markers()

        self.new_exercise()
        self.focus_set()

    def create_widgets(self):
        """Create basic window layout and the fixed widgets."""
        # pylint: disable=too-many-statements

        labels_f = tk.Frame(self)
        labels_f.pack(side=tk.TOP)

        label = tk.Label(labels_f, text="Scale:", font=SCALE_LABEL_FONT, padx=5)
        label.grid(row=0, column=0, columnspan=2, sticky=tk.E)
        self.scale_l = tk.Label(labels_f, font=SCALE_NAME_FONT, padx=5)
        self.scale_l.grid(row=0, column=2, columnspan=2, sticky=tk.W)

        label = tk.Label(labels_f, text="Current chord:", font=SCALE_LABEL_FONT, padx=5)
        label.grid(row=2, column=0, rowspan=2, sticky=tk.E)
        self.chord_d_l = tk.Label(labels_f, justify=tk.LEFT, font=SCALE_NAME_FONT, width=8)
        self.chord_d_l.grid(row=2, column=1, sticky=tk.W)
        self.chord_n_l = tk.Label(labels_f, justify=tk.LEFT, font=SCALE_NAME_FONT, width=8)
        self.chord_n_l.grid(row=3, column=1, sticky=tk.W)

        label = tk.Label(labels_f, text="Next chord:", font=SCALE_LABEL_FONT)
        label.grid(row=2, column=2, rowspan=2, sticky=tk.E)
        self.n_chord_d_l = tk.Label(labels_f, justify=tk.LEFT, font=SCALE_NAME_FONT, width=8)
        self.n_chord_d_l.grid(row=2, column=3, sticky=tk.W)
        self.n_chord_n_l = tk.Label(labels_f, justify=tk.LEFT, font=SCALE_NAME_FONT, width=8)
        self.n_chord_n_l.grid(row=3, column=3, sticky=tk.W)

        self.canvases_f = tk.Frame(self, padx=0, pady=0)
        self.top_canvas = tk.Canvas(self.canvases_f,
                                    height=CANVAS_HEIGHT / 2,
                                    width=CANVAS_WIDTH,
                                    bd=0,
                                    highlightthickness=0,
                                    relief='ridge',
                                    bg="white")
        self.top_canvas.pack(fill=tk.X, expand=1, pady=0, ipady=0)

        self.canvas = tk.Canvas(self.canvases_f,
                                height=CANVAS_HEIGHT,
                                width=CANVAS_WIDTH,
                                bd=0,
                                highlightthickness=0,
                                relief='ridge',
                                bg="white")
        self.canvas.pack(fill=tk.X, expand=1)

        self.bottom_canvas = tk.Canvas(self.canvases_f,
                                       height=CANVAS_HEIGHT / 2,
                                       width=CANVAS_WIDTH,
                                       bd=0,
                                       highlightthickness=0,
                                       relief='ridge',
                                       bg="white")
        self.bottom_canvas.pack(fill=tk.X, expand=1, pady=0, ipady=0)

        self.canvases_f.pack(fill=tk.X, expand=1, pady=0, ipady=0)

        tempo_f = tk.Frame(self)
        tempo_f.pack(expand=True, fill=tk.X)
        label = tk.Label(tempo_f, text="Tempo:")
        label.pack(side=tk.LEFT)
        self.tempo_s = tk.Scale(tempo_f,
                                from_=20.0,
                                to=200.0,
                                resolution=10,
                                orient=tk.HORIZONTAL)
        self.tempo_s.set(self.tempo)
        self.tempo_s["command"] = self.tempo_changed
        self.tempo_s.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.p_settings_f = tk.Frame(self)
        self.p_settings_f.pack()

        buttons_f = tk.Frame(self)
        buttons_f.pack()

        self.restart_b = tk.Button(buttons_f)
        self.restart_b["text"] = "Restart"
        self.restart_b["command"] = self.restart
        self.restart_b["state"] = tk.NORMAL
        self.restart_b.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("r", self.restart)

        self.play_b = tk.Button(buttons_f)
        self.play_b["text"] = "Play"
        self.play_b["command"] = self.play_pause
        self.play_b["state"] = tk.NORMAL
        self.play_b.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<space>", self.play_pause)

        separator = tk.Frame(self,
                             borderwidth=1,
                             height=3,
                             relief=tk.SUNKEN)
        separator.pack(expand=True, fill=tk.X)


        label = tk.Label(self, text="Next exercise settings: ")
        label.pack()

        self.e_settings_f1 = tk.Frame(self)
        self.e_settings_f1.pack()
        self.e_settings_f2 = tk.Frame(self)
        self.e_settings_f2.pack()

        buttons_f = tk.Frame(self)
        buttons_f.pack()

        self.new_b = tk.Button(buttons_f)
        self.new_b["text"] = "New Exercise"
        self.new_b["command"] = self.new_exercise
        self.new_b.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("n", self.new_exercise)

        self.quit_b = tk.Button(buttons_f)
        self.quit_b["text"] = "Quit"
        self.quit_b["command"] = self.master.destroy
        self.quit_b.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Control-Key-q>", lambda event: self.master.destroy())

        self.update_exercise_settings_widgets()
        self.update_player_settings_widgets()

    def update_exercise_settings_widgets(self): # pylint: disable=invalid-name
        """(Re)create exercise settings widgets.
        """
        for widget in self.e_settings_f1.winfo_children():
            widget.destroy()
        for widget in self.e_settings_f2.winfo_children():
            widget.destroy()

        label = tk.Label(self.e_settings_f1, text="Scale:")
        label.pack(side=tk.LEFT)

        if not self.scale_mode_v:
            self.scale_mode_v = tk.StringVar(self.e_settings_f1)
            if self.exercise:
                self.scale_mode_v.set(self.exercise.mode)
            else:
                self.scale_mode_v.set("major")
            self.scale_mode_v.trace("w", self.mode_changed)

        if not self.scale_root_v:
            self.scale_root_v = tk.StringVar(self.e_settings_f1)
            if self.exercise:
                self.scale_root_v.set(self.exercise.root)
            else:
                self.scale_root_v.set("<random>")

        options = ["<random>"] + list(SCALES[self.scale_mode_v.get()])
        self.scale_root_o = tk.OptionMenu(self.e_settings_f1,
                                          self.scale_root_v,
                                          *options)
        self.scale_root_o.pack(side=tk.LEFT)

        options = list(SCALES)
        self.scale_mode_o = tk.OptionMenu(self.e_settings_f1,
                                          self.scale_mode_v,
                                          *options)
        self.scale_mode_o.pack(side=tk.LEFT)

        label = tk.Label(self.e_settings_f1, text="Harmonization:")
        label.pack(side=tk.LEFT)

        if not self.harmonization_v:
            self.harmonization_v = tk.StringVar(self.e_settings_f1)
            if self.exercise:
                self.harmonization_v.set(self.exercise.harmonization)
            else:
                self.harmonization_v.set("triads")

        options = list(HARMONIZATION)
        self.harmonization_o = tk.OptionMenu(self.e_settings_f1,
                                             self.harmonization_v,
                                             *options)
        self.harmonization_o.pack(side=tk.LEFT)

        label = tk.Label(self.e_settings_f2, text="Progression:")
        label.pack(side=tk.LEFT)

        if not self.progression_v:
            self.progression_v = tk.StringVar(self.e_settings_f2)
            if self.exercise:
                self.progression_v.set(self.exercise.root)
            else:
                self.progression_v.set("<random>")
            self.progression_v.trace("w", self.progression_changed)

        options = ["<random>"] + get_progressions()
        self.progression_o = tk.OptionMenu(self.e_settings_f2,
                                           self.progression_v,
                                           *options)
        self.progression_o.pack(side=tk.LEFT)

        label = tk.Label(self.e_settings_f2, text="Exercise length:")
        label.pack(side=tk.LEFT)

        progression = self.progression_v.get()
        if self.exercise:
            length = self.exercise.length
        else:
            length = DEFAULT_LENGTH

        if progression == "<random>":
            options = ["{} bars".format(l) for l in range(5, 50, 5)]
        else:
            length, options = progression_length(progression, length, 60)
            options = ["{} bars".format(l) for l in options]

        if not self.length_v:
            self.length_v = tk.StringVar(self.e_settings_f2)
        self.length_v.set("{} bars".format(length))

        self.length_o = tk.OptionMenu(self.e_settings_f2,
                                      self.length_v,
                                      *options)
        self.length_o.pack(side=tk.LEFT)

    def update_player_settings_widgets(self):
        """(Re)create player settings widgets.

        Some of the OptionMenu widgets needs rebuilding due to option
        set depending on other settings and available resources.
        """

        if self.latency_s:
            latency = self.latency_s.get()
        else:
            latency = 0

        for widget in self.p_settings_f.winfo_children():
            widget.destroy()

        if self.player:
            label = tk.Label(self.p_settings_f, text="Backing track:")
            label.pack(side=tk.LEFT)

            if not self.track_v:
                self.track_v = tk.StringVar(self.p_settings_f)
                self.track_v.set(DEFAULT_TRACK)
                self.track_v.trace("w", self.track_changed)

            track_names = list(MAIN_TRACKS)
            self.track_o = tk.OptionMenu(self.p_settings_f,
                                         self.track_v,
                                         *track_names)
            self.track_o.pack(side=tk.LEFT)

            label = tk.Label(self.p_settings_f, text="MIDI port:")
            label.pack(side=tk.LEFT)

            if not self.midi_port_v:
                self.midi_port_v = tk.StringVar(self.p_settings_f)
                self.midi_port_v.set(self.player.port_name)
                self.midi_port_v.trace("w", self.midi_port_changed)
            else:
                self.midi_port_v.set(self.player.port_name)

            # pylint: disable=no-value-for-parameter
            self.midi_port_o = tk.OptionMenu(self.p_settings_f,
                                             self.midi_port_v,
                                             *self.player.available_ports)
            self.midi_port_o.pack(side=tk.LEFT)

            label = tk.Label(self.p_settings_f, text="Latency:")
            label.pack(side=tk.LEFT)

            # pylint: disable=no-value-for-parameter
            self.latency_s = tk.Scale(self.p_settings_f,
                                      from_=-500.0,
                                      to=500.0,
                                      resolution=1,
                                      orient=tk.HORIZONTAL)
            if latency:
                self.latency_s.set(latency)
            self.latency_s.pack(side=tk.LEFT)

    def midi_port_changed(self, *args_):
        """MIDI port selection widget change callback."""
        if self.player:
            self.player.change_port(self.midi_port_v.get())
        self.update_player_settings_widgets()

    def track_changed(self, *args_):
        """Backing track selection widget change callback."""
        if self.player:
            self.player.change_track(self.track_v.get())

    def tempo_changed(self, *args_):
        """Tempo change callback."""
        tempo = self.tempo_s.get()
        if self.paused_at:
            self.tempo = tempo
            return
        if self.start_time:
            now = time.time()
            rel_time = (now - self.start_time) * self.tempo
            self.start_time = now - rel_time / tempo
            self.tempo = tempo
            if self.player:
                self.player.change_tempo(tempo, self.start_time)

    def mode_changed(self, *args_):
        """Scale mode selection widget change callback."""
        root = self.scale_root_v.get()
        if root != "<random>":
            mode = self.scale_mode_v.get()
            root = normalize_scale_root(root, mode)
            self.scale_root_v.set(root)
        self.update_exercise_settings_widgets()

    def progression_changed(self, *args_):
        """Progression selection widget change callback."""
        self.update_exercise_settings_widgets()

    def draw_canvas(self):
        """Draw current exercise on the main canvas."""

        self.canvas.delete(tk.ALL)

        y_padding = (CANVAS_HEIGHT - BAR_HEIGHT) / 2

        # bars
        y = y_padding
        for i in range(LEAD_IN + self.exercise.length + 1):
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
        for i in range(self.exercise.length):
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
        canvas_length = width + 4096 # to be longer than any screen width

        self.canvas.config(scrollregion=(0, y, canvas_length, height),
                           xscrollincrement='1')

    def draw_markers(self):
        """Draw the current position markers (fixed)."""

        # position markers
        x0 = BEAT_OFFSET
        x1 = x0 - ARROW_HEAD_WIDTH
        x2 = x0 + ARROW_HEAD_WIDTH
        y0 = 0
        y1 = y0 + ARROW_LENGTH
        y2 = y0 + ARROW_HEAD_LENGTH

        h = CANVAS_HEIGHT / 2 # pylint: disable=invalid-name

        self.bottom_canvas.create_line(x0, y0, x0, y1)
        self.bottom_canvas.create_line(x0, y0, x1, y2)
        self.bottom_canvas.create_line(x0, y0, x2, y2)
        self.top_canvas.create_line(x0, h - y0, x0, h - y1)
        self.top_canvas.create_line(x0, h - y0, x1, h - y2)
        self.top_canvas.create_line(x0, h - y0, x2, h - y2)

    def restart(self, _event=None):
        """Restart the exercise."""
        self.start()

    def play_pause(self, _event=None):
        """Pause or continue the exercise."""
        if not self.start_time:
            print("Playing from the beginning")
            return self.start()
        tempo = self.tempo_s.get()
        now = time.time()
        if self.paused_at is not None:
            self.start_time = now - self.paused_at / tempo
            print("Unpausing")
            self.paused_at = None
            track = self.track_v.get()
            self.player.start(self.exercise, self.start_time, track, tempo)
            self.play_b["text"] = "Pause"
            self.canvas.after(10, self.progress)
        else:
            self.player.stop()
            self.paused_at = (now - self.start_time) * tempo
            self.play_b["text"] = "Play"
            print("Paused at {:.3f}".format(self.paused_at))

    def start(self):
        """Start the exercise."""

        if self.player:
            self.player.stop()

        self.play_b["text"] = "Pause"
        self.chord_d_l["text"] = "–"
        self.chord_n_l["text"] = "–"
        self.n_chord_d_l["text"] = "–"
        self.n_chord_n_l["text"] = "–"

        self.canvas.xview_moveto(0)

        song_length = (LEAD_IN + self.exercise.length) * self.exercise.bar_duration
        print("Song length: {}s".format(song_length))

        if self.latency_s:
            latency = self.latency_s.get() / 1000.0
        else:
            latency = 0

        self.paused_at = None
        self.start_time = time.time() + latency + 0.001
        if self.player:
            track = self.track_v.get()
            tempo = self.tempo_s.get()
            self.player.start(self.exercise, self.start_time, track, tempo)

        self.end_time = self.start_time + song_length
        self.progress()

    def progress(self):
        """Update window as the exercise progresses.

        Scroll the canvas and show current chords.
        """

        if not self.start_time:
            # exercise stopped
            return

        now = time.time()
        total_bars = LEAD_IN + self.exercise.length
        if self.latency_s:
            latency = self.latency_s.get() / 1000.0
        else:
            latency = 0

        tempo = self.tempo_s.get()

        if self.paused_at is not None:
            pos = self.paused_at - latency * tempo
        else:
            pos = now - self.start_time - latency
            if pos < 0:
                pos = 0
            pos *= tempo

        bar = int(pos // self.exercise.bar_duration)
        beat = (pos % self.exercise.bar_duration) / self.exercise.beat_duration

        if bar != self.bar and bar < total_bars:
            self.bar = bar
            if bar >= LEAD_IN:
                chord_degree = self.exercise.progression[bar - LEAD_IN] + 1
                self.chord_d_l["text"] = ROMAN[chord_degree - 1]
                self.chord_n_l["text"] = "?"
            if bar >= LEAD_IN - 1 and bar < total_bars - 1:
                chord_degree = self.exercise.progression[bar - LEAD_IN + 1] + 1
                self.n_chord_d_l["text"] = ROMAN[chord_degree - 1]
                self.n_chord_n_l["text"] = "?"


        if beat != self.beat and bar < total_bars:
            self.beat = beat
            if bar >= LEAD_IN and beat >= CHORD_NAME_DELAY:
                chord_name = self.exercise.chord_names[bar - LEAD_IN]
                self.chord_n_l["text"] = chord_name

        canvas_target = int(bar * BAR_LENGTH + beat * BEAT_LENGTH)
        canvas_x = int(self.canvas.canvasx(0))

        if canvas_target != canvas_x:
            self.canvas.xview_scroll(canvas_target - canvas_x, tk.UNITS)
        if now < self.end_time and not self.paused_at:
            self.canvas.after(10, self.progress)

    def new_exercise(self, _event=None):
        """Generate new exercise."""
        if self.player:
            self.player.stop()
        if self.scale_mode_v:
            mode = self.scale_mode_v.get()
        else:
            mode = None
        if self.scale_root_v:
            root = self.scale_root_v.get()
            if root == "<random>":
                root = None
        else:
            root = None
        if self.harmonization_v:
            harmonization = self.harmonization_v.get()
        else:
            harmonization = "triads"
        if self.length_v:
            length = int(self.length_v.get().split(" ", 1)[0])
        else:
            length = DEFAULT_LENGTH
        if self.progression_v:
            progression = self.progression_v.get()
            if progression == "<random>":
                progression = None
        else:
            progression = None
        self.exercise = Exercise(root=root,
                                 mode=mode,
                                 harmonization=harmonization,
                                 length=length,
                                 progression=progression)
        self.start_time = None
        self.end_time = None
        self.bar = None
        self.beat = None
        self.canvas.xview_moveto(0)
        self.chord_d_l["text"] = "–"
        self.chord_n_l["text"] = "–"
        self.n_chord_d_l["text"] = "–"
        self.n_chord_n_l["text"] = "–"
        self.scale_l["text"] = self.exercise.scale_name
        self.draw_canvas()
        self.play_b["text"] = "Play"

def main():
    """Main entry point."""
    time_res = check_time_resolution()
    print("Detected time measurement resolution: {:0.6f} ms"
          .format(time_res * 1000))
    if time_res > 0.020:
        print("WARNING: inadequate time measurement resolution!")
    time_res = check_time_resolution(time.perf_counter)
    print("Detected precise time measurement resolution: {:0.6f} ms"
          .format(time_res * 1000))
    if time_res > 0.001:
        print("WARNING: inadequate precise time measurement resolution!")
    sleep_prec = check_sleep_precision()
    if sleep_prec > 0.010:
        print("WARNING: inadequate thread sleep time precision!")
    root_w = tk.Tk()
    root_w.title("Chord Exercise Partner")
    app = CEPApplication(master=root_w)
    app.mainloop()
