"""The 2D view of the system: bodies, labels, zoom (scroll) and pan (drag)."""
import tkinter as tk

BG = "#0b0e17"

class OrbitCanvas(tk.Canvas):
    def __init__(self, master):
        super().__init__(master, bg=BG, highlightthickness=0)
        self.scale = 100.0  # pixels per length unit
        self.cx, self.cy = 0.0, 0.0  # world coordinates at the centre of the view

        self.bind("<ButtonPress-1>", self._pan_start)

    # ---- view ----
    def fit(self, system):
        """Zoom so every body is visible."""
        w, h = max(self.winfo_width(), 400), max(self.winfo_height(), 400)
        extent = max(abs(system.pos).max(initial=0) * 1.2, 1e-3)
        self.scale = min(w, h) / (2 * extent)
        self.cx, self.cy = 0.0, 0.0

    def to_screen(self, x, y):
        w, h = self.winfo_width(), self.winfo_height()
        return w / 2 + (x - self.cx) * self.scale, h / 2 - (y - self.cy) * self.scale

    def _pan_start(self, e):
        self._drag = (e.x, e.y)

    # ---- drawing ----
    def draw(self, system, show_labels=True, show_trails=False, selected=None):
        self.delete("all")
        # TODO: trails (needs position history from Simulation.history)
        for i in range(len(system)):
            sx, sy = self.to_screen(system.pos[2 * i], system.pos[2 * i + 1])
            r = system.radii[i]
            col = system.colors[i]
            self.create_oval(sx - r, sy - r, sx + r, sy + r, fill=system.colors[i], outline="")
            if i == selected:
                self.create_oval(sx - r - 4, sy - r - 4, sx + r + 4, sy + r + 4, outline="#ffffff")
            if show_labels:
                self.create_text(sx + r + 4, sy - r - 2, text=system.names[i], anchor="sw",
                                 fill="#c8cbe0", font=("Helvetica", 10))
            if show_trails:
                #unpack it here like the others
                all_x = system.pos_past[0::2]
                all_y = system.pos_past[1::2]
                x_current = all_x[i::len(system)]
                y_current = all_y[i::len(system)]
                #overwrite to always have starting position, to always have 4 points
                x_current = [x_current[0], *x_current]
                y_current = [y_current[0], *y_current]

                #head against a wall approach
                poslist = []
                for j in range(len(x_current)):
                    c_x, c_y =  self.to_screen(x_current[j], y_current[j])
                    poslist.append(c_x)
                    poslist.append(c_y)

                if len(poslist) >= 1000: # probably need to sync this to dt step - to be done when i update the git
                    system.pos_past = system.pos_past[12:] #probably should move this to update. normalize wrt step/frame?

                self.create_line(*poslist, fill=col, width = r/2, smooth = 1)

