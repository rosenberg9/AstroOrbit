import numpy as np
import pytest
 
from astroorbit.analysis.stability import close_encounters
from astroorbit.physics import integrators
from astroorbit.physics.forces import newtonian
from astroorbit.physics.units import ASTRO
 
 
def test_close_encounters_straight_line():
    masses = np.array([0.0, 0.0])
    pos = np.array([0.0, 0.0, -5.0, 1.0])
    vel = np.array([0.0, 0.0, 1.0, 0.0])
    dt = 1e-3
 
    def accel(p):
        return newtonian(p, masses, ASTRO.G)
 
    found = False

    for _ in range(5000):  # t = 5, closest approach r = 1.0
        pos, vel = integrators.rk4(pos, vel, accel, dt)
        if close_encounters(pos, threshold=1.1):
            found = True
            break
    assert found
 