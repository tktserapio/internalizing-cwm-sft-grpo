"""
Scenarios for Y (triangular board, BOARD_SIZE=5).
P0 is Black, P1 is White. Action format: "x,y".
Valid cells: x>=0, y>=0, x+y < BOARD_SIZE (i.e. x+y <= 4).
Sides: LEFT (x==0), TOP (y==0), DIAGONAL (x+y==4).
Win: connect all three sides with a chain of adjacent stones.
"""

# P0 (Black) wins: path along y=0 from (0,0) to (4,0)
# (0,0) touches LEFT+TOP; (4,0) touches TOP+DIAGONAL → group has all three sides
_P0_WIN = ["0,0", "0,4", "1,0", "1,3", "2,0", "0,3", "3,0", "0,2", "4,0"]

# P1 (White) wins: path along diagonal x+y=4 from (4,0) to (0,4)
# (4,0) touches TOP+DIAGONAL; (0,4) touches LEFT+DIAGONAL → group has all three sides
_P1_WIN = ["0,0", "4,0", "1,0", "3,1", "2,0", "2,2", "3,0", "1,3", "4,1", "0,4"]

SCENARIOS = [
    {
        "name": "Non-terminal after first stone",
        "actions": ["0,0"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Four stones in a row not terminal (missing third side)",
        "actions": ["0,0", "4,0", "1,0", "3,1", "2,0"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "P0 wins: path along top edge connects all three sides",
        "actions": _P0_WIN,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: path along diagonal connects all three sides",
        "actions": _P1_WIN,
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Non-terminal after three alternating moves",
        "actions": ["0,0", "4,0", "1,0"],
        "checks": {"terminal": False, "current_player": 1},
    },
]
