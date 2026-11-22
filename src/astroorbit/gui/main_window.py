"""Main window: wires the mode bar, canvas, plots and side panels to a Simulation."""
import tkinter as tk
import numpy as np
from dataclasses import replace
from tkinter import ttk

from astroorbit.gui.canvas import OrbitCanvas
from astroorbit.gui.help import Tooltip
from astroorbit.gui.panels.bodies import BodyPanel
from astroorbit.gui.panels.controls import ControlPanel
from astroorbit.gui.plots import PlotsPanel
from astroorbit.modes import MODES, load_presets
from astroorbit.gui.panels.dropdowns import DROPDOWNS
from astroorbit.physics.units import ASTRO, NBODY, UnitSystem, UNIT_SYSTEMS, convert
from astroorbit.physics.body import Body
from astroorbit.physics.system import System
from astroorbit.simulation import Simulation, State
from astroorbit.physics.integrators import INTEGRATORS

FRAME_MS = 16


class MainWindow:
    def __init__(self, root):
        self.root = root
        root.title("AstroOrbit")
        root.geometry("1200x780")
        self.mode = None
        self.unit = UNIT_SYSTEMS["astro"] #default to astro
        self.sim = None
        self.presets = {}
        self.message = ""  # shown in the status bar until replaced
        self.mode_var = tk.StringVar(value="planet")
        self.unit_system_var = tk.StringVar(value="astro")#ASTRO

        self._build()
        self.load_mode("planet")
        self._tick()

    # ------------------------------------------------------------ layout ---
    def _build(self):
        top = ttk.Frame(self.root, padding=(10, 6))
        top.pack(fill="x")
        ttk.Label(top, text="AstroOrbit", font=("Helvetica", 16, "bold")).pack(side="left")
        # for key, mode in MODES.items():
        #     rb = ttk.Radiobutton(top, text=mode.label, value=key, variable=self.mode_var,
        #                          command=lambda: self.load_mode(self.mode_var.get()))
        #     rb.pack(side="left", padx=(16, 0))
        #     Tooltip(rb, mode.description)

        #to top add dropdown menus, same loop different functionality
        for key, dd in DROPDOWNS.items():
            ddm = ttk.Menubutton(top, text = dd.label)
            ddm.menu = tk.Menu(ddm, tearoff=False)  
            ddm["menu"]= ddm.menu  
            for submenu_name, submenu_key in zip(dd.submenu_names, dd.submenu_keys):
                if key == "Mode": #can do that but seems like a lazy way to go
                    ddm.menu.add_radiobutton(label = submenu_name, value = submenu_key, variable=self.mode_var, 
                                             command = lambda: self.load_mode(self.mode_var.get()))
                elif key == "Units":
                    ddm.menu.add_radiobutton(label = submenu_name, value = submenu_key, variable=self.unit_system_var, 
                                             command = lambda: self.load_units(self.unit_system_var.get())) #, command = lambda: self.load_units(self.unit_system) #based on button, load unit system
                elif key == "Plot Body Selection":
                    ddm.menu.add_checkbutton(label = submenu_name)
            ddm.pack(side = "left", padx=(16, 0))
            Tooltip(ddm, dd.description)

            # Status bar container
            self.status_frame = tk.Frame(self.root,bg="#0d101b",height=17)
            self.status_frame.pack(side="bottom", fill="x")
            self.status_frame.pack_propagate(False)
            # White simulation information
            self.status = tk.Label(
                self.status_frame,
                anchor="w",
                font=("Helvetica", 14),
                fg="white",
                bg="#0d101b",
                padx=10,
                pady= 6
            )
            self.status.pack(side="left")
            # Red messages and errors
            self.message_label = tk.Label(
                self.status_frame,
                anchor="w",
                font=("Helvetica", 14),
                fg="#ff4444",
                bg="#0d101b",
                padx=5,
                pady= 6
            )
        self.message_label.pack(side="left")

        main = ttk.PanedWindow(self.root, orient="horizontal")
        main.pack(fill="both", expand=True)

        left = ttk.PanedWindow(main, orient="vertical")
        self.canvas = OrbitCanvas(left)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.on_view_change = self.redraw
        self.plots = PlotsPanel(left)
        left.add(self.canvas, weight=4)
        left.add(self.plots, weight=1)

        right = ttk.Frame(main, padding=10)
        self.controls = ControlPanel(right, on_preset=self.load_preset,
                                     on_integrator=self.set_integrator,
                                     on_command=self.command, on_view=self.redraw, on_dt=self.apply_dt)
        self.controls.pack(fill="x")
        self.body_panel = BodyPanel(right, on_select=self.select_body,
                                    on_add=self.add_body, on_apply=self.apply_body,
                                    on_delete=self.delete_body, units=self.unit, sim_units=ASTRO)
        self.body_panel.pack(fill="both", expand=True, pady=(10, 0))

        main.add(left, weight=1)
        main.add(right, weight=0)

    # ------------------------------------------------------- modes/presets ---
    def load_mode(self, key):
        self.mode = MODES[key]
        self.body_panel.update_units(self.unit, self.mode.units)
        self.presets = load_presets(key)
        self.controls.set_presets(list(self.presets))
        self.controls.set_integrators(list(INTEGRATORS.keys()), self.mode.default_integrator)
        self.plots.set_mode(self.mode)
        if self.presets:
            self.load_preset(self.controls.preset.get())

    def load_preset(self, name):
        preset = self.presets[name]
        system = System([Body(**b) for b in preset["bodies"]])
        self.sim = Simulation(system, self.mode,
                            integrator=self.controls.integrator.get(), dt=preset["dt"])
        self.controls.set_dt(self.sim.dt)
        self.message = preset["description"]
        self.plots.clear()
        self.root.update_idletasks()
        self.canvas.fit(self.sim.system)
        self.canvas.clear_trails()
        self.refresh_bodies()

    def set_integrator(self, name):
        self.sim.set_integrator(name)
        self.redraw()

    # ------------------------------------------------------------ units ---
    def load_units(self, key):
        self.unit = UNIT_SYSTEMS[key]
        self.body_panel.update_units(self.unit)
        self.redraw()

    # ------------------------------------------------------------ controls ---
    def apply_dt(self, dt):
        self.sim.dt = dt
        self.redraw()

    def command(self, cmd):
        self.message = ""
        getattr(self.sim, cmd)()  # start / pause / resume / reset
        if cmd in ("start", "reset"):
            self.plots.clear()
        if cmd == "reset":
            self.refresh_bodies()
            self.canvas.clear_trails()
        self.redraw()

    def _advance(self):
        try:
            self.sim.advance(self.controls.speed.get())
        except NotImplementedError as exc:
            self.sim.pause()
            self.message = f"Not implemented yet: {exc}"

    # -------------------------------------------------------------- bodies ---
    def refresh_bodies(self, keep=None):
        self.body_panel.set_bodies(self.sim._initial.bodies(), keep)
        self.redraw()

    def select_body(self, i):
        self.refresh_bodies(keep=i)

    def add_body(self, values):
        n = len(self.sim.system)
        values["name"] = values["name"] or f"Body {n}"
        color = "#{:06x}".format(np.random.randint(0, 0x1000000))
        mass = values["mass"]
        # Size of body follows log scale (physical would be M^1/3)
        # Earth mass give 3 Pixel radius, Sun mass gives 9 pixel
        radius = 9 - 6 * np.log10(1 / mass) / np.log10(1 / 3.0e-6)
        radius = np.clip(radius, 3, None)
        self.sim.add_body(Body(**values, color=color, radius_px=radius))
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
            return
        if len(self.sim.system) > 1:
            self.sim.remove_body(i)
            self.canvas.remove_trail(i)
            self.refresh_bodies()

    # ---------------------------------------------------------------- loop ---
    def _tick(self):
        if self.sim and self.sim.state is State.RUNNING:
            self._advance()
            if self.sim.error:
                self.message, self.sim.error = self.sim.error, None
                self.plots.clear()
                self.canvas.clear_trails()
                self.refresh_bodies()
                self.root.after(FRAME_MS, self._tick)
                return
            if self.sim.ejected:
                self.message = f"{', '.join(self.sim.ejected)} ejected. Press Reset to start again"
          
            colors = dict(zip(self.sim.system.names, self.sim.system.colors))
            self.plots.refresh(self.sim.history, colors)
            self.redraw()
        self.root.after(FRAME_MS, self._tick)

    def redraw(self):
        if not self.sim:
            return
        self.canvas.draw(self.sim.system,
                         show_labels=self.controls.show_labels.get(),
                         show_trails=self.controls.show_trails.get(),
                         selected=self.body_panel.selected())
        self.controls.update_buttons(self.sim.state)
        self.update_status()

    def update_status(self):
        s, u = self.sim, self.mode.units
        text = (
            f"{self.mode.label}  ·  {s.state.value}  ·  "
            f"t = {s.t:.3f} {u.time}  ·  "
            f"{s.integrator.__name__}  ·  "
            f"{len(s.system)} bodies")
    
        self.status.config(text=text)
        self.message_label.config(text=f"|  {self.message}" if self.message else "")

def main():
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
