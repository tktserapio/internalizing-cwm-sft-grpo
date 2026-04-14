"""
Scenarios for Matching Pennies.
P0 wins when both players choose the same (match); P1 wins on mismatch.
"""

SCENARIOS = [
    {
        "name": "P0 wins: both choose Heads",
        "actions": ["H", "H"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: P0 Heads, P1 Tails (mismatch)",
        "actions": ["H", "T"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "P1 wins: P0 Tails, P1 Heads (mismatch)",
        "actions": ["T", "H"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "P0 wins: both choose Tails",
        "actions": ["T", "T"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "Non-terminal after P0 moves",
        "actions": ["H"],
        "checks": {"terminal": False, "current_player": 1},
    },
]
