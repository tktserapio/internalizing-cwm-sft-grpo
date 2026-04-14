"""
Scenarios for Battleship (4x4 board).
Ships: one 2-cell ship and one 1-cell ship per player (TOTAL_SHIP_CELLS=3).
Chance actions: "place_p0:SHIPS" then "place_p1:SHIPS"
  Encoding: cells as "RC" joined by "_" per ship, ships joined by "|"
  e.g. "place_p0:00_01|22" = P0's 2-cell ship at (0,0)-(0,1) and 1-cell ship at (2,2)
Player actions: "fire_R_C"
P0 fires first after setup. Win: hit all 3 opponent ship cells.
"""

# Fixed placement: P0 ships at (0,0)-(0,1) and (2,2); P1 ships at (1,0)-(1,1) and (3,3)
_SETUP = ["place_p0:00_01|22", "place_p1:10_11|33"]

SCENARIOS = [
    {
        "name": "Non-terminal after setup: P0 to fire",
        "actions": _SETUP,
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "Non-terminal after P0 miss: P1 to fire",
        "actions": _SETUP + ["fire_0_0"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Non-terminal mid-game: P0 has 2 hits, P1 has 1 hit",
        "actions": _SETUP + ["fire_1_0", "fire_2_2", "fire_1_1"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "P0 wins: hits all 3 P1 ship cells (P1 misses in between)",
        "actions": _SETUP + ["fire_1_0", "fire_0_3", "fire_1_1", "fire_1_3", "fire_3_3"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: hits all 3 P0 ship cells (P0 misses in between)",
        "actions": _SETUP + ["fire_0_2", "fire_0_0", "fire_0_3", "fire_0_1", "fire_2_3", "fire_2_2"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
]
