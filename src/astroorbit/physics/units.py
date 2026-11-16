"""Unit systems. Each one fixes the value of G, so physics code never hard-codes it."""
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class UnitSystem:
    name: str
    length: str
    time: str
    mass: str
    G: float
    FIELDS_DISPLAY: tuple

astro_display = ("Name", "Mass (solar mass)", "x (AU)", "y (AU)", "vx (AU/year)", "vy (AU/year)")
si_display = ("Name", "Mass (kg)", "x (km)", "y (km)", "vx (km/s)", "vy (km/s)")
nbody_display = ("Name", "Mass (mass unit)", "x (length unit)", "y (length unit)", "vx (length/time)", "vy (length/time)")
ASTRO = UnitSystem("astro", "AU", "yr", "Msun", 4 * math.pi ** 2, astro_display)
SI = UnitSystem("SI", "m", "s", "kg", 6.67430e-11, si_display)
NBODY = UnitSystem("nbody", "L", "T", "M", 1.0, nbody_display)  # G = 1, handy for few-body / chaos setups

def ASTRO_convert(a_mass, a_x, a_y, a_vx, a_vy, new_coord_name): #since only displayed values should change, not calculations, these 2 functions should be enough
    if new_coord_name == "astro":
        return (a_mass, a_x, a_y, a_vx, a_vy)
    elif new_coord_name == "SI":
        si_mass = a_mass * 1.989e+30 #m_sol -> kg
        si_x = a_x * 1.496e+8 #AU -> m
        si_y = a_y * 1.496e+8
        si_vx = a_vx * 4.74372 #AU/yr to km/s
        si_vy = a_vy* 4.74372
        si_vals = (si_mass, si_x, si_y, si_vx, si_vy)
        return si_vals
    elif new_coord_name == "nbody": #how to transform to nbody?
        nb_mass = a_mass #* 1.989e+30 #m_sol -> kg
        nb_x = a_x #* 1.496e+8 #AU -> m
        nb_y = a_y #* 1.496e+8
        nb_vx = a_vx #* 4.74372 #AU/yr to km/s
        nb_vy = a_vy#* 4.74372
        nb_vals = (nb_mass, nb_x, nb_y, nb_vx, nb_vy)
        return nb_vals


    return None

def ASTRO_to_NBODY():
    return None

UNIT_SYSTEMS = {u.name: u for u in (ASTRO, SI, NBODY)}
