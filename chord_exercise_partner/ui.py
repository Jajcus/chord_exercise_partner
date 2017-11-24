#!/usr/bin/python3

"""C.E.P. UI implementation."""

import time
import tkinter as tk

from .exercise import Exercise, LEAD_IN, EXERCISE_LENGTH, TEMPO
from .player import CompPlayer, MIDINotAvailable
from .tracks import MAIN_TRACKS, DEFAULT_TRACK

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

CHORD_NAME_DELAY = 2 # beats

class CEPApplication(tk.Frame):
    """Application window."""
    # pylint: disable=too-many-ancestors
    def __init__(self, master=None):
        super().__init__(master)
        self.start_time = None
        self.end_time = None
        self.bar = None
        self.beat = None
        self.exercise = None

        self.track_v = None
        self.track_o = None
        self.midi_port_v = None
        self.midi_port_o = None

        try:
            self.player = CompPlayer()
        except MIDINotAvailable as err:
            print("MIDI player not available:", err)
            self.player = None

        self.pack(expand=1, fill=tk.BOTH)
        self.create_widgets()
        self.draw_markers()

        self.new_exercise()

    def create_widgets(self):
        """Create basic window layout and the fixed widgets."""
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
        """(Re)create settings widgets.

        Some of the OptionMenu widgets needs rebuilding due to option
        set depending on other settings and available resources.
        """
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

            # pylint: disable=no-value-for-parameter
            self.midi_port_o = tk.OptionMenu(self.settings_f,
                                             self.midi_port_v,
                                             *self.player.available_ports)
            self.midi_port_o.pack(side=tk.LEFT)

    def midi_port_changed(self, *args_):
        """MIDI port selection widget change callback."""
        if self.player:
            self.player.change_port(self.midi_port_v.get())
        self.update_settings_widgets()

    def draw_canvas(self):
        """Draw current exercise on the main canvas."""

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

    def start(self):
        """Start the exercise."""

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
        """Update window as the exercise progresses.

        Scroll the canvas and show current chords.
        """

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
        """Generate new exercise."""
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

def main():
    """Main entry point."""
    root_w = tk.Tk()
    root_w.title("Chord Exercise Partner")
    app = CEPApplication(master=root_w)
    app.mainloop()
