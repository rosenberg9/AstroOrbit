"""Physics checks for the integrators. Skipped until each step() is implemented."""
import pytest

from astroorbit.analysis.elements import orbital_elements  # 

REF = {"a": 1.7857142857142856, "e": 0.43999999999999995, "period": 14.993320610381373}
 
RTOL = 1e-12
 
 
def test_orbital_elements_vs_rebound():

    # One eccentric body around a central body, G = 1
    G = 1.0
    mu = G * (1.0 + 0.0)
    result = orbital_elements((1.0, 0.0), (0.0, 1.2), mu)
 
    for key in ("a", "e", "period"):
        assert result[key] == pytest.approx(REF[key], rel=RTOL)
 