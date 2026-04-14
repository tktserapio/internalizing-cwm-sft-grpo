"""
Scenarios for Backgammon.
Chance action: "D_X_Y" (dice roll, X and Y are 1-6).
Player actions: "FROM/TO" or "FROM/TO,FROM/TO,..." for multi-move sequences.
  FROM/TO: point numbers 1-24, "bar" (entering from bar), or "off" (bearing off).
P0 moves counterclockwise (decreasing point numbers), P1 clockwise (increasing).
After D_X_Y: if X>=Y → P0 moves, if X<Y → P1 moves.
Doubles give 4 dice (e.g., D_3_3 → [3,3,3,3]).
"""

# Two-move sequence used across scenarios
_P0_MOVE = "13/7,7/2"  # P0 uses dice [6,5]: 13→7 (die=6), 7→2 (die=5)
_P1_MOVE = "19/20,1/3"  # P1 uses dice [1,2]: 19→20, 1→3

SCENARIOS = [
    {
        "name": "Dice roll D_6_5: P0 to move (d1>=d2)",
        "actions": ["D_6_5"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "After P0 moves: back to CHANCE for next roll",
        "actions": ["D_6_5", _P0_MOVE],
        "checks": {"terminal": False, "current_player": -1},
    },
    {
        "name": "Dice roll D_1_2: P1 to move (d1<d2)",
        "actions": ["D_6_5", _P0_MOVE, "D_1_2"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "After P1 moves: back to CHANCE",
        "actions": ["D_6_5", _P0_MOVE, "D_1_2", _P1_MOVE],
        "checks": {"terminal": False, "current_player": -1},
    },
    {
        "name": "Doubles D_3_3: P0 gets 4 dice (d1==d2 → P0 moves)",
        "actions": ["D_6_5", _P0_MOVE, "D_1_2", _P1_MOVE, "D_3_3"],
        "checks": {"terminal": False, "current_player": 0},
    },
]
