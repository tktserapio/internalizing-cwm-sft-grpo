"""
Scenarios for Quadranto (4x4 grid).
Chance actions: "place_p0:r,c" (quadrant 1: rows 0-1, cols 0-1),
                "place_p1:r,c" (quadrant 4: rows 2-3, cols 2-3).
Player actions: "Up", "Down", "Left", "Right", "Stay".
Win: move onto opponent's cell. Draw: 20 total player moves.
"""

# P0 catches P1: P0 marches Down,Down,Right,Right; P1 Stays each time
_P0_WINS = [
    "place_p0:0,0", "place_p1:2,2",
    "Down", "Stay", "Down", "Stay", "Right", "Stay", "Right",
]

# P1 catches P0: P0 Stays each time; P1 marches Up,Up,Left,Left
_P1_WINS = [
    "place_p0:0,0", "place_p1:2,2",
    "Stay", "Up", "Stay", "Up", "Stay", "Left", "Stay", "Left",
]

# Draw: 20 total moves with neither player ever meeting
# P0 bounces between (0,0)↔(0,1); P1 bounces between (2,2)↔(2,3)
_DRAW = ["place_p0:0,0", "place_p1:2,2"]
for _i in range(5):
    _DRAW += ["Right", "Right", "Left", "Left"]

SCENARIOS = [
    {
        "name": "Non-terminal after placement",
        "actions": ["place_p0:0,0", "place_p1:2,2"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "P0 Stay passes turn to P1",
        "actions": ["place_p0:0,0", "place_p1:2,2", "Stay"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "P0 wins: moves onto P1 cell",
        "actions": _P0_WINS,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: moves onto P0 cell",
        "actions": _P1_WINS,
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Draw: 20 total moves with no catch",
        "actions": _DRAW,
        "checks": {"terminal": True, "rewards_sign": [0, 0]},
    },
]
