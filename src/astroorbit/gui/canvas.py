"""The 2D view of the system: bodies, labels, zoom (scroll) and pan (drag)."""
import tkinter as tk

BG = "#0b0e17"

class OrbitCanvas(tk.Canvas):
    def __init__(self, master):
        super().__init__(master, bg=BG, highlightthickness=0)
        self.scale = 100.0  # pixels per length unit
        self.cx, self.cy = 0.0, 0.0  # world coordinates at the centre of the view

        self.bind("<ButtonPress-1>", self._pan_start)
        self.bind("<B1-Motion>", self._pan_move)
        self.bind("<MouseWheel>", self._zoom)                          # macOS / Windows
        self.bind("<Button-4>", lambda e: self._zoom(e, 1))            # Linux
        self.bind("<Button-5>", lambda e: self._zoom(e, -1))
        self._last = None

        self.trail_len = 100      
        self._trails = []

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

    def _pan_move(self, e):
        x0, y0 = self._drag
        self.cx -= (e.x - x0) / self.scale
        self.cy += (e.y - y0) / self.scale
        self._drag = (e.x, e.y)
        self._redraw()

    def _zoom(self, e, delta=None):
        f = 1.1 if (delta if delta is not None else e.delta) > 0 else 1 / 1.1
        w, h = self.winfo_width(), self.winfo_height()
        wx = self.cx + (e.x - w / 2) / self.scale      # world point under cursor
        wy = self.cy - (e.y - h / 2) / self.scale
        self.scale *= f
        self.cx = wx - (e.x - w / 2) / self.scale      # keep it under cursor
        self.cy = wy + (e.y - h / 2) / self.scale
        self._redraw()

    def _redraw(self):
        if self._last:
            self.draw(*self._last)

    def clear_trails(self):
        self._trails = []

    def _record(self, system):
        n = len(system)
        while len(self._trails) < n:
            self._trails.append([])
        del self._trails[n:]
        
        for i, tr in enumerate(self._trails):
            p = (system.pos[2 * i], system.pos[2 * i + 1])
            if not tr or tr[-1] != p:
                tr.append(p)
                if len(tr) > self.trail_len:
                    del tr[0]

    def remove_trail(self, i):
        if i < len(self._trails):
            del self._trails[i]

    # ---- drawing ----
    def draw(self, system, show_labels=True, show_trails=False, selected=None):
        self._last = (system, show_labels, show_trails, selected)
        self.delete("all")
        if show_trails:
            self._record(system)
            for tr, col, r in zip(self._trails, system.colors, system.radii):
                if len(tr) >= 2:
                    pts = [c for x, y in tr for c in self.to_screen(x, y)]
                    self.create_line(*pts, fill=col, width=max(1, r / 2))
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
                self._record(system)
                for i, tr in enumerate(self._trails):
                    if len(tr) >= 2:
                        pts = [c for x, y in tr for c in self.to_screen(x, y)]
                        self.create_line(*pts, fill=system.colors[i],
                                        width=max(1, system.radii[i] / 2))

