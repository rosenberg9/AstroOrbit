"""Body list and editor: select, add, edit and delete bodies."""
import tkinter as tk
from tkinter import ttk
import math
from astroorbit.gui.help import HELP, Tooltip
from astroorbit.physics.units import convert

FIELDS = ("name", "mass", "x", "y", "vx", "vy")
KINDS = {"mass": "mass", "x": "length", "y": "length", "vx": "velocity", "vy": "velocity"}

class BodyPanel(ttk.LabelFrame):
    """Calls on_select(i), on_add(), on_apply(i, values), on_delete(i)."""

    def __init__(self, master, on_select, on_add, on_apply, on_delete, units, sim_units):
        super().__init__(master, text="Bodies", padding=8)
        self.listbox = tk.Listbox(self, height=6, exportselection=False)
        self.listbox.pack(fill="x")
        self.listbox.bind("<<ListboxSelect>>", lambda e: self._selected_changed(on_select))
        self.listbox.bind("<Button-1>", lambda e: self._click(e, on_select))

        self.vars = {}
        self.errors = {}
        grid = ttk.Frame(self)
        grid.pack(fill="x", pady=6)
        grid.columnconfigure(1, weight=1)
        self.labels = []
        for row, key in enumerate(FIELDS):
            this_label = ttk.Label(grid, text=units.FIELDS_DISPLAY[row], width=22)
            this_label.grid(row=row, column=0, sticky="w") #pack here to be able to update the labels
            self.labels.append(this_label)
            var = tk.StringVar()
            entry = ttk.Entry(grid, textvariable=var)
            entry.grid(row=row, column=1, sticky="ew", pady=1)
            if key in HELP:
                Tooltip(entry, HELP[key])
            self.vars[key] = var
            error = ttk.Label(grid, foreground="#e0483e")
            error.grid(row=row, column=2, sticky="w", padx=(4, 0))
            self.errors[key] = error

        row = ttk.Frame(self)
        row.pack(fill="x")
        self.add_button = ttk.Button(row, text="Add",width = -1, command=lambda: self._add(on_add))
        self.add_button.pack(side="left", expand=True, fill="x")
        ttk.Button(row, text="Apply", width = -1, command=lambda: self._apply(on_apply)).pack(
            side="left", expand=True, fill="x")
        ttk.Button(row, text="Delete", width = -1, command=lambda: self._delete(on_delete)).pack(
            side="left", expand=True, fill="x")
        self._bodies = []
        self.units, self.sim_units = units, sim_units


    def set_bodies(self, bodies, keep=None):
        self._bodies = bodies
        self.listbox.delete(0, "end")
        for b in bodies:
            self.listbox.insert("end", b.name)
        if keep is not None and keep < len(bodies):
            self.listbox.selection_set(keep)
        self._fill()

    def update_units(self, units, sim_units=None):
        self.units = units
        self.sim_units = sim_units or self.sim_units
        for n, l in enumerate(self.labels):
            l["text"] = units.FIELDS_DISPLAY[n]
        self._fill()

    def _click(self, e, on_select):
        i = self.listbox.nearest(e.y)
        if i in self.listbox.curselection():
            self.listbox.selection_clear(0, "end")
            self._fill()
            on_select(None)
            return "break" 
        
    def selected(self):
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def values(self):
        """Editor contents as a dict. Bad numbers get a red message and the result is None."""
        result = {"name": self.vars["name"].get()}
        valid = True
        for key in FIELDS[1:]:
            try:
                v = float(self.vars[key].get())
                ok = math.isfinite(v)
                result[key] = convert(v, KINDS[key], self.units, self.sim_units)
            except ValueError:
                ok = False
            self.errors[key].config(text="" if ok else "must be number")
            valid = valid and ok
        return result if valid else None

    def _fill(self):
        i = self.selected()
        for error in self.errors.values():
            error.config(text="")
        for key, var in self.vars.items():
            value = "" if i is None else getattr(self._bodies[i], key)
            if i is not None and key in KINDS:
                value = convert(value, KINDS[key], self.sim_units, self.units)
            var.set(value if isinstance(value, str) else f"{value:.6g}")
        self.add_button.config(text="Add" if i is None else "Duplicate")

    def _selected_changed(self, on_select):
        self._fill()
        on_select(self.selected())

    def _add(self, on_add):
        values = self.values()
        if values is not None:
            on_add(values)

    def _apply(self, on_apply):
        i, values = self.selected(), self.values()
        if i is not None and values is not None:
            on_apply(i, values)

    def _delete(self, on_delete):
        i = self.selected()
        if i is not None:
            on_delete(i)
