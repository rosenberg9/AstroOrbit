
"""Dropdown Menus with the parameters they will change"""
from __future__ import annotations
from dataclasses import dataclass
from astroorbit.physics.units import UnitSystem, UNIT_SYSTEMS
from astroorbit.modes import MODES
#from astroorbit.gui.main_window import MainWindow

@dataclass(frozen=True)
class DDMenu:
    key: str
    label: str
    description: str
    submenu_names: list[str]
    submenu_keys: list[str]

DROPDOWNS = {
    "Mode": DDMenu(
        key = "mode",
        label = "Mode",
        description = "Menu to choose which mode should be loaded",
        submenu_names = [mode.label for key, mode in MODES.items()], #make sure all are loaded
        submenu_keys = [mode.key for key, mode in MODES.items()],

    ),
    "Units": DDMenu(
        key = "units",
        label = "Units",
        description = "Menu to choose which Units should be loaded",
        submenu_names = [i for i in UNIT_SYSTEMS.keys()],
        submenu_keys = [UNIT_SYSTEMS[i].name for i in UNIT_SYSTEMS.keys()],
    ),
    # "Statistics": DDMenu(
    #     key = "statistics",
    #     label = "Statistics",
    #     description = "Additional Statistics to be viewed in a new window",
    #     submenu_names = ["See Initial Values", "Average change of the Semimajor Axis", "c", "d"],
    #     submenu_keys = ["a", "b", "c", "d"],
    #     functionality = dummyfunc,
    #     units = None, #placeholder values
    #     plots = None,
    # ),
    # "Plot Body Selection": DDMenu(
    #     key = "pbselection",
    #     label = "Plot Body Selection",
    #     description = "Select which bodies should be tracked by plotters below",
    #     submenu_names = ["a", "b", "c", "d"],
    #     submenu_keys = ["a", "b", "c", "d"],
    #     functionality = dummyfunc,
    #     units = None, #placeholder values
    #     plots = None,
    # ),
}
