"""Unit systems. 

N-body units: G = M = L = 1, with M = 1 Msun and L = 1 AU chosen as the physical
scale. Then T = sqrt(L^3 / (G M)) = 1 yr / 2pi and 1 L/T = 2pi AU/yr ~ 29.8 km/s.
"""
import math
from dataclasses import dataclass

G_SI = 6.67430e-11                                   # m^3 kg^-1 s^-2
AU, YR, MSUN = 1.495978707e11, 3.15576e7, 1.98847e30  # m, s, kg


@dataclass(frozen=True)
class UnitSystem:
    name: str
    length: str
    time: str
    mass: str
    G: float
    length_si: float  # one length unit, in metres
    time_si: float    # one time unit, in seconds
    mass_si: float    # one mass unit, in kg

    def factor(self, kind):
        L, T, M = self.length_si, self.time_si, self.mass_si
        return {"length": L, "time": T, "mass": M,
                "velocity": L / T, "energy": M * L ** 2 / T ** 2}[kind]

    @property
    def FIELDS_DISPLAY(self):
        v = f"{self.length}/{self.time}"
        return ("Name", f"Mass ({self.mass})", f"Initial X ({self.length})", f"Initial Y ({self.length})",
                f"Initial Velocity X ({v})", f"Initial Velocity Y ({v})")


def convert(value, kind, frm, to):
    """value in system frm -> system to. kind: length, time, mass, velocity, energy."""
    return value * frm.factor(kind) / to.factor(kind)


ASTRO = UnitSystem("astro", "AU", "yr", "Msun", 4 * math.pi ** 2, AU, YR, MSUN)
SI = UnitSystem("SI", "km", "s", "kg", G_SI * 1e-9, 1e3, 1.0, 1.0)
NBODY = UnitSystem("nbody", "L", "T", "M", 1.0, AU, (AU ** 3 / (G_SI * MSUN)) ** 0.5, MSUN)

UNIT_SYSTEMS = {u.name: u for u in (ASTRO, SI, NBODY)}