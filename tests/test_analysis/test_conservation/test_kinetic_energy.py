"""Physics checks for the integrators. Skipped until each step() is implemented."""
import math
import numpy as np
import pytest

from astroorbit.analysis.conservation import kinetic_energy

G = 1.0
MASSES = [1.0, 2.0, 3.0, 4.0]
VEL = [1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 0.0]
 
REBOUND_KE = +12.5
 
 
@pytest.mark.skipif(REBOUND_KE is None, reason="REBOUND reference not set")
def test_kinetic_energy_vs_rebound():
    assert kinetic_energy(VEL, MASSES) == pytest.approx(REBOUND_KE, rel=1e-12)
 