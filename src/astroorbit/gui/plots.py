"""Plots of quantities over time (orbital elements, energy error, ...)."""
from tkinter import ttk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

BG = "#0b0e17"
TEXT = "#c8cbe0"
REFRESH_EVERY = 10  # redraw once every this many frames: matplotlib is slow

MIN_SPAN = {"a": 0.1, "e": 0.1, "r": 0.1, "E": 0.1}  # smallest y-range per plot: stops noise being magnified

HISTORY_KEYS = {
    "Semi-major axis": "a",
    "Eccentricity": "e",
    "Energy error": "energy_error",
    "Distance to Sun": "r",
    "Total System Energy": "E",
}

class PlotsPanel(ttk.LabelFrame):
    def __init__(self, master):
        # title row: "Plots" + a multi-select menu, used as the frame's label
        header = ttk.Frame(master)
        ttk.Label(header, text="Plots").pack(side="left")
        button = ttk.Menubutton(header, text="Select ▾")
        button.pack(side="left", padx=(8, 0))
        menu = tk.Menu(button, tearoff=False)
        button["menu"] = menu
        self.show = {}
        for title in HISTORY_KEYS:
            var = tk.BooleanVar()
            menu.add_checkbutton(label=title, variable=var, command=self._layout)
            self.show[title] = var

        super().__init__(master, labelwidget=header, padding=4)
        self.fig = Figure(figsize=(8, 2), facecolor=BG)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.axes = {}   # history key -> matplotlib axes
        self.lines = {}  # (history key, line name) -> matplotlib line
        self.frame = 0
        self._last = None  # (history, colors) of the last refresh, to redraw after a toggle

    def set_mode(self, mode):
        """Tick the mode's default plots, then build them."""
        for title, var in self.show.items():
            var.set(title in mode.plots)
        self._layout()

    def _layout(self):
        """One small plot per ticked entry."""
        titles = [t for t, var in self.show.items() if var.get()]
        self.fig.clear()
        self.axes, self.lines = {}, {}
        for n, title in enumerate(titles):
            ax = self.fig.add_subplot(1, len(titles), n + 1, facecolor=BG)
            ax.set_title(title, color=TEXT, fontsize=9)
            ax.tick_params(colors=TEXT, labelsize=7)
            ax.yaxis.get_offset_text().set_fontsize(7)
            for spine in ax.spines.values():
                spine.set_color("#444a60")
            self.axes[HISTORY_KEYS[title]] = ax
        self.fig.subplots_adjust(left=0.06, right=0.98, bottom=0.14, top=0.86, wspace=0.28)
        if self._last:
            self._draw(*self._last)
        else:
            self.canvas.draw_idle()

    def clear(self):
        """Remove all lines, e.g. after Reset or a new preset."""
        for line in self.lines.values():
            line.remove()
        self.lines = {}
        self._last = None
        self.canvas.draw_idle()

    def refresh(self, history, colors):
        """Called every frame; redraws once every REFRESH_EVERY frames."""
        self._last = (history, colors)
        self.frame += 1
        if self.frame % REFRESH_EVERY == 0:
            self._draw(history, colors)

    def _draw(self, history, colors):
        for key, ax in self.axes.items():
            for name, points in history[key].items():
                if (key, name) not in self.lines:
                    self.lines[key, name] = ax.plot([], [], lw=1, color=colors.get(name, TEXT))[0]
                t, values = zip(*points)
                self.lines[key, name].set_data(t, values)
            ax.relim()
            ax.autoscale_view()
            low, high = ax.get_ylim()
            span = MIN_SPAN.get(key, 0)
            if high - low < span:
                middle = (low + high) / 2
                ax.set_ylim(middle - span / 2, middle + span / 2, auto=True)
        self.canvas.draw_idle()