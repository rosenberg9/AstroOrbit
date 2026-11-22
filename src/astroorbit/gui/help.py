"""Contextual help: all tooltip texts in one place, plus a small Tooltip widget."""
import tkinter as tk

HELP = {
    "integrator": "Numerical method used to advance the system in time.\n"
                  "Euler: 1st order, energy drifts.\n"
                  "RK4: 4th order, accurate but slowly drifts.\n"
                  "Leapfrog: 2nd order, symplectic: energy error stays bounded.",
    "preset": "Choose a preset system of bodies to load.",
    "dt": "Time step of the integrator, in the mode's time unit. "
          "Smaller is more accurate but slower.",
    "speed": "How many integration steps are computed per animation frame.",
    "mass": "Mass of the body",
    "x": "X Position of the body",
    "y": "Y Position of the body",
    "vx": "X Velocity of the body",
    "vy": "Y Velocity of the body",
    "trails": "Draw the recent path of each body.",
    "labels": "Show body names next to them on the canvas.",
    "start": "Start the simulation from the current state.",
    "pause": "Pause the simulation, keeping the current state.",
    "resume": "Resume the simulation from the current state.",
    "reset": "Reset the simulation to the initial conditions (keeping added bodies).",
    "canvas": "The main canvas for displaying the simulation. Use mouse to zoom and pan.",
    "plots": "Select which quantities to plot over time. "
             "Each plot shows the history of the selected quantity.",
}


class Tooltip:
    def __init__(self, widget, text):
        self.widget, self.text, self.tip = widget, text, None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _show(self, _event):
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(self.tip, text=self.text, justify="left", wraplength=280,
                 background="#ffffe0", foreground="#000000", relief="solid",
                 borderwidth=1, padx=6, pady=4).pack()

    def _hide(self, _event):
        if self.tip:
            self.tip.destroy()
            self.tip = None
