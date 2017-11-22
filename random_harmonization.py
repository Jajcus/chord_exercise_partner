#!/usr/bin/python3

import time
import random

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

def scale_name(root):
    flats = FLATS[root]
    return "{}-major".format(NOTES[flats][root])

def chord_name(root, degree):
    chord_note, chord_quality = HARMONISATION[degree]
    chord_root = (root + chord_note) % 12
    chord_name = NOTES[FLATS[root]][chord_root]
    return chord_name +  chord_quality

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

class ChordTester(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.start_time = None
        self.end_time = None
        self.bar = None
        self.beat = None
        self.exercise = None

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

        self.canvases = tk.Frame(self, padx=0, pady=0)
        self.top_canvas = tk.Canvas(self.canvases,
                                height=CANVAS_HEIGHT / 2,
                                width=CANVAS_WIDTH,
                                bd=0, highlightthickness=0, relief='ridge',
                                bg="white")
        self.top_canvas.pack(fill=tk.X, expand=1, pady=0, ipady=0)

        self.canvas = tk.Canvas(self.canvases,
                                height=CANVAS_HEIGHT,
                                width=CANVAS_WIDTH,
                                bd=0, highlightthickness=0, relief='ridge',
                                bg="white")
        self.canvas.pack(fill=tk.X, expand=1)

        self.bottom_canvas = tk.Canvas(self.canvases,
                                height=CANVAS_HEIGHT / 2,
                                width=CANVAS_WIDTH,
                                bd=0, highlightthickness=0, relief='ridge',
                                bg="white")
        self.bottom_canvas.pack(fill=tk.X, expand=1, pady=0, ipady=0)

        self.canvases.pack(fill=tk.X, expand=1, pady=0, ipady=0)

        self.buttons = tk.Frame(self)
        self.buttons.pack(side=tk.BOTTOM)

        self.start_b = tk.Button(self.buttons)
        self.start_b.pack(side=tk.LEFT, padx=5, pady=5)

        self.quit_b = tk.Button(self.buttons)
        self.quit_b["text"] = "Quit"
        self.quit_b["command"] = self.master.destroy
        self.quit_b.pack(side=tk.RIGHT, padx=5, pady=5)

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
        self.start_b["text"] = "New Exercise"
        self.start_b["command"] = self.new_exercise
        song_length = ((LEAD_IN + EXERCISE_LENGTH) * 4.0) * 60 / TEMPO
        print("Song length: {}s".format(song_length))
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
        self.start_b["command"] = self.start

root_w = tk.Tk()
app = ChordTester(master=root_w)
app.mainloop()

