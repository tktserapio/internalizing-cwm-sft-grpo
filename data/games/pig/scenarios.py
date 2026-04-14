"""
Scenarios for Pig.
Player actions: "roll" (then chance gives "1"-"6") or "hold".
Rolling a 1 (pig) loses the turn total and passes to the other player.
Holding adds the turn total to the player's permanent score; turn passes.
First to reach 100+ points after holding wins.
"""

# Helper: build P0 win sequence by rolling 6 seventeen times then holding
# 17 * 6 = 102 >= 100 → P0 wins without P1 ever acting
_P0_SEVENTEEN_SIXES = []
for _ in range(17):
    _P0_SEVENTEEN_SIXES += ["roll", "6"]
_P0_WIN = _P0_SEVENTEEN_SIXES + ["hold"]

# P0 pigged once, then P1 wins: P0 rolls 1 (pigged), P1 rolls 6 seventeen times then holds
_P1_WIN = ["roll", "1"] + list(_P0_SEVENTEEN_SIXES) + ["hold"]

SCENARIOS = [
    {
        "name": "Rolling a 1 (pig) loses turn total and passes to P1",
        "actions": ["roll", "1"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Holding after one 5 passes to P1",
        "actions": ["roll", "5", "hold"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Rolling passes back to player (not P1's turn yet)",
        "actions": ["roll", "6"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "P0 wins: 17 sixes then hold (102 points)",
        "actions": _P0_WIN,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: P0 pigged, P1 rolls 17 sixes then holds (102 points)",
        "actions": _P1_WIN,
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
]
