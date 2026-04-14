"""
Scenarios for Pentago (6x6, win=5 in a row).
Player actions: "mark(row,col)_rotate_Q_D"
  mark: 'x' (P0) or 'o' (P1)
  row,col: 0-indexed position on the 6x6 board
  Q: quadrant 0=top-left, 1=top-right, 2=bottom-left, 3=bottom-right
  D: 'CW' (clockwise) or 'CCW' (counter-clockwise)
Quadrant boundaries: Q0=(r0-2,c0-2), Q1=(r0-2,c3-5), Q2=(r3-5,c0-2), Q3=(r3-5,c3-5).
When the rotated quadrant is empty the rotation has no effect.
"""

# P0 builds column 0 (rows 0-4); both players rotate Q3 which stays empty.
_P0_WIN = [
    "x(0,0)_rotate_3_CW", "o(0,3)_rotate_3_CW",
    "x(1,0)_rotate_3_CW", "o(1,3)_rotate_3_CW",
    "x(2,0)_rotate_3_CW", "o(2,3)_rotate_3_CW",
    "x(3,0)_rotate_3_CW", "o(0,4)_rotate_3_CW",
    "x(4,0)_rotate_3_CW",  # 5th x in col 0 → P0 wins
]

# P1 builds column 3 (rows 0-4); both players rotate Q2 which stays empty.
_P1_WIN = [
    "x(0,0)_rotate_2_CW", "o(0,3)_rotate_2_CW",
    "x(0,1)_rotate_2_CW", "o(1,3)_rotate_2_CW",
    "x(0,2)_rotate_2_CW", "o(2,3)_rotate_2_CW",
    "x(1,0)_rotate_2_CW", "o(3,3)_rotate_2_CW",
    "x(1,1)_rotate_2_CW", "o(4,3)_rotate_2_CW",  # 5th o in col 3 → P1 wins
]

SCENARIOS = [
    {
        "name": "Non-terminal after first move: P1 to move",
        "actions": ["x(0,0)_rotate_3_CW"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Non-terminal after 4 moves (2 full rounds): P0 to move",
        "actions": _P0_WIN[:4],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "Non-terminal after 7 moves: P1 to move before P0 wins",
        "actions": _P0_WIN[:7],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "P0 wins: 5 in column 0, rotations applied to empty Q3",
        "actions": _P0_WIN,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: 5 in column 3, rotations applied to empty Q2",
        "actions": _P1_WIN,
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
]
