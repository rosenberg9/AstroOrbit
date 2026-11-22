"""Main window: builds the layout and connects the panels to a Simulation."""
import tkinter as tk
from dataclasses import replace
from functools import partial
from tkinter import ttk
import tkinter.font as tkfont
import numpy as np

from astroorbit.gui.canvas import OrbitCanvas
from astroorbit.gui.help import HELP, Tooltip
from astroorbit.gui.panels.bodies import BodyPanel
from astroorbit.gui.panels.controls import ControlPanel
from astroorbit.gui.plots import PlotsPanel
from astroorbit.modes import MODES, load_presets
from astroorbit.physics.body import Body
from astroorbit.physics.integrators import INTEGRATORS
from astroorbit.physics.system import System
from astroorbit.physics.units import ASTRO, UNIT_SYSTEMS, convert
from astroorbit.simulation import Simulation, State

FRAME_MS = 16          # time between animation frames, in ms (~60 per second)
STATUS_BG = "#0d101b"

UI_FONT = ("Helvetica", 15)    # family, size for all widgets

def display_radius(mass):
    """Pixel radius on a log scale: Earth mass -> 3 px, Sun mass -> 9 px."""
    return max(3, 9 - 6 * np.log10(1 / mass) / np.log10(1 / 3.0e-6))

class MainWindow:
    def __init__(self, root):
        self.root = root
        root.title("AstroOrbit")
        root.geometry("1000x1000")
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            tkfont.nametofont(name).configure(family=UI_FONT[0], size=UI_FONT[1])
            root.option_add("*TCombobox*Listbox.font", UI_FONT)   # the list that drops down

        self.sim = None
        self.mode = MODES["planet"]
        self.unit = UNIT_SYSTEMS["astro"]   # units shown to the user
        self.presets = {}
        self.message = ""                   # red text in the status bar
        self.mode_var = tk.StringVar(value="planet")
        self.unit_var = tk.StringVar(value="astro")

        self._build()
        self.load_mode("planet")
        self._tick()

    # ------------------------------------------------------------ layout ---
    def _build(self):
        top = ttk.Frame(self.root, padding=(10, 6))
        top.pack(fill="x")
        ttk.Label(top, text="AstroOrbit", font=("Helvetica", 32, "bold")).pack(side="left")
        self._menu(top, "Mode", self.mode_var, {m.label: k for k, m in MODES.items()}, self.load_mode)
        self._menu(top, "Units", self.unit_var, {k: k for k in UNIT_SYSTEMS}, self.load_units)

        # status bar at the bottom: white simulation info, then red messages
        bar = tk.Frame(self.root, bg=STATUS_BG)
        bar.pack(side="bottom", fill="x")
        self.status = self._status_label(bar, "white", font=("Helvetica", 22))
        self.message_label = self._status_label(bar, "#ff4444", font=("Helvetica", 22))

        main = ttk.PanedWindow(self.root, orient="horizontal")
        main.pack(fill="both", expand=True)

        left = ttk.PanedWindow(main, orient="vertical")      # canvas above, plots below
        self.canvas = OrbitCanvas(left)
        Tooltip(self.canvas, HELP["canvas"])
        self.plots = PlotsPanel(left)
        left.add(self.canvas, weight=4)
        left.add(self.plots, weight=1)

        right = ttk.Frame(main, padding=10, width=330)                   # control panels on the right
        right.pack_propagate(False)       
        self.controls = ControlPanel(right, on_preset=self.load_preset, on_integrator=self.set_integrator,
                                     on_command=self.command, on_view=self.redraw, on_dt=self.apply_dt)
        self.controls.pack(fill="x")
        self.body_panel = BodyPanel(right, on_select=self.select_body, on_add=self.add_body,
                                    on_apply=self.apply_body, on_delete=self.delete_body,
                                    units=self.unit, sim_units=ASTRO)
        self.body_panel.pack(fill="both", expand=True, pady=(10, 0))

        main.add(left, weight=1)
        main.add(right, weight=0)

    def _menu(self, parent, title, var, items, when_chosen):
        """A dropdown in the top bar. items = {text shown: key passed to when_chosen}."""
        button = ttk.Menubutton(parent, text=title)
        menu = tk.Menu(button, tearoff=False)
        button["menu"] = menu
        for text, key in items.items():
            menu.add_radiobutton(label=text, value=key, variable=var, command=partial(when_chosen, key))
        button.pack(side="left", padx=(16, 0))

    def _status_label(self, bar, colour, font):
        label = tk.Label(bar, anchor="w", font=font, fg=colour, bg=STATUS_BG, padx=5, pady=6)
        label.pack(side="left")
        return label

    # updating the presets, units, integrators when the mode changes
    def load_mode(self, key):
        self.mode = MODES[key]
        self.body_panel.update_units(self.unit, self.mode.units)
        self.presets = load_presets(key)
        self.controls.set_presets(list(self.presets))
        self.controls.set_integrators(list(INTEGRATORS), self.mode.default_integrator)
        self.plots.set_mode(self.mode)
        if self.presets:
            self.load_preset(self.controls.preset.get())

    #updating the bodies when preset is changed
    def load_preset(self, name):
        preset = self.presets[name]
        system = System([Body(**b) for b in preset["bodies"]])
        self.sim = Simulation(system, self.mode, integrator=self.controls.integrator.get(), dt=preset["dt"])
        self.controls.set_dt(self.sim.dt)
        #self.message = preset["description"]
        self.root.update_idletasks()          # so the canvas knows its size before fitting
        self.canvas.fit(self.sim.system)
        self._clear_view()

    #changing the input units
    def load_units(self, key):
        self.unit = UNIT_SYSTEMS[key]
        self.body_panel.update_units(self.unit)
        self.redraw()

    # changing integrator
    def set_integrator(self, name):
        self.sim.set_integrator(name)
        self.redraw()

    #changing dt timestep
    def apply_dt(self, dt):
        self.sim.dt = dt
        self.redraw()

    def command(self, cmd):
        """Start / Pause / Resume / Reset buttons."""
        self.message = ""
        getattr(self.sim, cmd)()              # e.g. "pause" runs self.sim.pause()
        if cmd == "start":
            self.plots.clear()
        if cmd == "reset":
            self._clear_view()
        self.redraw()

    def _clear_view(self):
        """Empty the plots and trails and re-read the bodies (new preset, reset, error)."""
        self.plots.clear()
        self.canvas.clear_trails()
        self.refresh_bodies()

    def refresh_bodies(self, keep=None):
        self.body_panel.set_bodies(self.sim.initial_bodies(), keep)
        self.redraw()

    def select_body(self, i):
        self.refresh_bodies(keep=i)

    def add_body(self, values):
        n = len(self.sim.system)
        values["name"] = values["name"] or f"Body {n}"
        colour = "#{:06x}".format(np.random.randint(0, 0x1000000))   # random colour
        self.sim.add_body(Body(**values, color=colour, radius_px=display_radius(values["mass"])))
        self.refresh_bodies(keep=n)

    def apply_body(self, i, values):
        self.sim.update_body(i, replace(self.sim.initial_bodies()[i], **values))
        if self.sim.t > 0:
            self.message = "Change applies from the next Reset"
        self.refresh_bodies(keep=i)

    def delete_body(self, i):
        if i == 0 and self.mode.key in ("planet", "comet"):
            self.message = "The Sun can't be removed in this mode"
            self.redraw()
        elif len(self.sim.system) > 1:
            self.sim.remove_body(i)
            self.canvas.remove_trail(i)
            self.refresh_bodies()

    def _tick(self):
        """Runs every frame: advance the simulation, then redraw."""
        if self.sim and self.sim.state is State.RUNNING:
            self.sim.advance(self.controls.speed.get())
            if self.sim.error:                # bodies too close: the sim has reset itself
                self.message, self.sim.error = self.sim.error, None
                self._clear_view()
            else:
                if self.sim.ejected:
                    self.message = f"{', '.join(self.sim.ejected)} ejected. Press Reset to start again"
                colours = dict(zip(self.sim.system.names, self.sim.system.colors))
                self.plots.refresh(self.sim.history, colours)
                self.redraw()
        self.root.after(FRAME_MS, self._tick)

    def redraw(self):
        if not self.sim:
            return
        self.canvas.draw(self.sim.system, show_labels=self.controls.show_labels.get(),
                         show_trails=self.controls.show_trails.get(), selected=self.body_panel.selected())
        self.controls.update_buttons(self.sim.state)
        s = self.sim
        t = convert(s.t, "time", self.mode.units, self.unit)
        self.status.config(text=f"{self.mode.label}  ·  {s.state.value}  ·  t = {t:.2f} {self.unit.time}  ·  "
                                f"{s.integrator.__name__}  ·  {len(s.system)} bodies")
        self.message_label.config(text=f"|  {self.message}" if self.message else "")

def main():
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()