"""
Scenarios for Converge (5x5 grid).
P0 starts at (0,0) and (0,4); P1 starts at (4,0) and (4,4).
Actions: "move (r1,c1) to (r2,c2)" or "pass".
Win: move a piece to center (2,2). Draw: 50 total turns.
"""

# P0 wins: P0 piece diagonally to center in 2 moves; P1 moves away
_P0_WINS = [
    "move (0,0) to (1,1)",   # P0 moves toward center
    "move (4,0) to (3,1)",   # P1 moves away from center
    "move (1,1) to (2,2)",   # P0 reaches center → P0 wins
]

# P1 wins: P1 piece diagonally to center in 2 moves; P0 moves away
_P1_WINS = [
    "move (0,0) to (1,0)",   # P0 moves but not toward center
    "move (4,4) to (3,3)",   # P1 moves toward center
    "move (1,0) to (2,0)",   # P0 moves but not to center (no stun on P1)
    "move (3,3) to (2,2)",   # P1 reaches center → P1 wins
]

# Draw: 50 total turns, P0 bounces (0,0)↔(0,1), P1 bounces (4,0)↔(4,1)
_DRAW = []
for _i in range(25):
    if _i % 2 == 0:
        _DRAW += ["move (0,0) to (0,1)", "move (4,0) to (4,1)"]
    else:
        _DRAW += ["move (0,1) to (0,0)", "move (4,1) to (4,0)"]

SCENARIOS = [
    {
        "name": "Non-terminal after first move",
        "actions": ["move (0,0) to (1,1)"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "P0 wins: reaches center (2,2)",
        "actions": _P0_WINS,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: reaches center (2,2)",
        "actions": _P1_WINS,
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Draw: 50 total turns without anyone reaching center",
        "actions": _DRAW,
        "checks": {"terminal": True, "rewards_sign": [0, 0]},
    },
    {
        "name": "Non-terminal after three alternating moves",
        "actions": ["move (0,0) to (1,1)", "move (4,0) to (3,1)", "move (0,4) to (1,3)"],
        "checks": {"terminal": False, "current_player": 1},
    },
]
