
"""Dropdown Menus with the parameters they will change"""
from dataclasses import dataclass
from astroorbit.physics.units import ASTRO, NBODY, UnitSystem, UNIT_SYSTEMS
from astroorbit.modes import MODES, load_presets
#from astroorbit.gui.main_window import MainWindow
from astroorbit.physics.integrators import INTEGRATORS

def dummyfunc(*args):
    return None



@dataclass(frozen=True)
class DDMenu:
    key: str
    label: str
    description: str
    submenu_names: list[str]
    submenu_keys: list[str]
    functionality: function
    units: UnitSystem #those probably should be not in modes, but in the dropdown menu, and then apply changes to whole [rpgram upon selection there, no?]
    plots: tuple = ()  # quantities offered in the plots panel


DROPDOWNS = {
    "Mode": DDMenu(
        key = "mode",
        label = "Mode",
        description = "Menu to choose which mode should be loaded",
        submenu_names = [mode.label for key, mode in MODES.items()], #make sure all are loaded
        submenu_keys = [mode.key for key, mode in MODES.items()],
        functionality = dummyfunc,#load_mode, #pointer to a function
        #args?
        units = None, #placeholder values
        plots = None,
    ),
    "Units": DDMenu(
        key = "units",
        label = "Units",
        description = "Menu to choose which Units should be loaded",
        submenu_names = [i for i in UNIT_SYSTEMS.keys()],
        submenu_keys = [UNIT_SYSTEMS[i].name for i in UNIT_SYSTEMS.keys()],
        functionality = dummyfunc,
        units = None, #placeholder values - list\dict of units
        plots = None,
    ),
    "Statistics": DDMenu(
        key = "statistics",
        label = "Statistics",
        description = "Additional Statistics to be viewed in a new window",
        submenu_names = ["See Initial Values", "Average change of the Semimajor Axis", "c", "d"],
        submenu_keys = ["a", "b", "c", "d"],
        functionality = dummyfunc,
        units = None, #placeholder values
        plots = None,
    ),
    "Plot Body Selection": DDMenu(
        key = "pbselection",
        label = "Plot Body Selection",
        description = "Select which bodies should be tracked by plotters below",
        submenu_names = ["a", "b", "c", "d"],
        submenu_keys = ["a", "b", "c", "d"],
        functionality = dummyfunc,
        units = None, #placeholder values
        plots = None,
    ),
}
