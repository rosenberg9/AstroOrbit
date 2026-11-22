"""Simulation controls: preset, integrator, time step, speed, start/pause/resume/reset."""
import math
import tkinter as tk
from functools import partial
from tkinter import ttk

from astroorbit.gui.help import HELP, Tooltip
from astroorbit.simulation import State

MIN_LOGDT, MAX_LOGDT = -5, -1          # dt slider range: 1e-5 to 1e-1
SUPERSCRIPT = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")

# which button is clickable in each state (Reset always is)
ACTIVE = {State.STOPPED: "start", State.RUNNING: "pause", State.PAUSED: "resume"}

class ControlPanel(ttk.LabelFrame):
    """The 'Simulation' box. It only draws widgets; when the user changes something it
    calls the function MainWindow gave it: on_preset(name), on_integrator(name),
    on_command(cmd), on_view(), on_dt(dt)."""

    def __init__(self, master, on_preset, on_integrator, on_command, on_view, on_dt):
        super().__init__(master, text="Simulation", padding=8)  # build the box itself first
        self.on_preset, self.on_integrator, self.on_dt = on_preset, on_integrator, on_dt

        # values the rest of the app reads with .get()
        self.preset = tk.StringVar()
        self.integrator = tk.StringVar()
        self.speed = tk.IntVar(value=5)
        self.show_trails = tk.BooleanVar(value=False)
        self.show_labels = tk.BooleanVar(value=True)

        self.preset_box = self._dropdown("Preset", self.preset, self._preset_chosen)
        self.integrator_box = self._dropdown("Integrator", self.integrator, self._integrator_chosen)

        # dt slider: its value is the power of ten, so dt = 10 ** value
        self.dt_label = ttk.Label(self)
        self.dt_label.pack(anchor="w", pady=(6, 0))
        self.dt_scale = tk.Scale(self, from_=MIN_LOGDT, to=MAX_LOGDT, resolution=0.01,
                                 orient="horizontal", showvalue=False, highlightthickness=0,
                                 command=self._dt_moved)
        self.dt_scale.pack(fill="x")
        Tooltip(self.dt_scale, HELP["dt"])
        ticks = ttk.Frame(self, height=18)
        ticks.pack(fill="x")
        for power in range(MIN_LOGDT, MAX_LOGDT + 1):
            x = 0.04 + 0.92 * (power - MIN_LOGDT) / (MAX_LOGDT - MIN_LOGDT)  # under the slider
            text = "10" + str(power).translate(SUPERSCRIPT)                   # -3 -> 10⁻³
            ttk.Label(ticks, text=text, font=("Helvetica", 10)).place(relx=x, anchor="n")

        row = self._row()
        ttk.Label(row, text="speed").pack(side="left")
        speed = ttk.Scale(row, from_=1, to=50, variable=self.speed, orient="horizontal")
        speed.pack(side="left", fill="x", expand=True, padx=(4, 0))
        Tooltip(speed, HELP["speed"])


        # one button that says Start / Pause / Resume depending on the state, plus Reset
        self.on_command = on_command
        self.action = "start"
        row = self._row()
        self.run_button = ttk.Button(row, text="Start", command=self._run_clicked)
        self.run_button.pack(side="left", expand=True, fill="x")
        Tooltip(self.run_button, HELP["run"])
        reset = ttk.Button(row, text="Reset", command=partial(on_command, "reset"))
        reset.pack(side="left", expand=True, fill="x")
        Tooltip(reset, HELP["reset"])

        row = self._row()
        for name, var in (("trails", self.show_trails), ("labels", self.show_labels)):
            cb = ttk.Checkbutton(row, text=name.title(), variable=var, command=on_view)
            cb.pack(side="left", padx=(0, 10))
            Tooltip(cb, HELP[name])

    # ---- small helpers for building ----
    def _row(self):
        """An empty horizontal strip to put widgets side by side."""
        row = ttk.Frame(self)
        row.pack(fill="x", pady=(6, 0))
        return row

    def _dropdown(self, title, var, when_chosen):
        """A label plus a read-only dropdown list; when_chosen runs on every pick."""
        ttk.Label(self, text=title).pack(anchor="w", pady=(6, 0))
        box = ttk.Combobox(self, textvariable=var, state="readonly")
        box.pack(fill="x")
        box.bind("<<ComboboxSelected>>", when_chosen)
        Tooltip(box, HELP[title.lower()])
        return box

    # update preset when the user changes something in the dropdowns or slider
    def _preset_chosen(self, event):
        self.on_preset(self.preset.get())

    # update integrator when the user changes something in the dropdowns or slider
    def _integrator_chosen(self, event):
        self.on_integrator(self.integrator.get())

    def _run_clicked(self):
        self.on_command(self.action)          # "start", "pause" or "resume"

    # update dt when the user changes something in the dropdowns or slider
    def _dt_moved(self, value):
        dt = 10 ** float(value)
        self.dt_label.config(text=f"dt = {dt:.2g}")
        self.on_dt(dt)

    # needed by MainWindow
    def set_dt(self, dt):
        self.dt_scale.set(math.log10(dt))
        self.dt_label.config(text=f"dt = {dt:.2g}")

    def set_presets(self, names):
        self.preset_box["values"] = names
        self.preset.set(names[0] if names else "")

    def set_integrators(self, names, default):
        self.integrator_box["values"] = names
        self.integrator.set(default)

    def update_buttons(self, state):
        self.action = ACTIVE[state]
        self.run_button.config(text=self.action.title())