"""
Scenarios for Connect Four (6 rows × 7 columns).
P0 uses 'x', P1 uses 'o'.  Action format: x{col} or o{col} (col 0-6).
Pieces fall to the lowest available row (gravity).
Win: 4 in a row (horizontal, vertical, or diagonal).
Draw: board full, no winner.
"""

SCENARIOS = [
    {
        "name": "P0 wins: vertical in column 0",
        "actions": ["x0", "o1", "x0", "o1", "x0", "o1", "x0"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P0 wins: horizontal cols 1-4 (bottom row)",
        "actions": ["x3", "o3", "x4", "o4", "x2", "o2", "x1"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: horizontal cols 0-3 (bottom row)",
        "actions": ["x4", "o0", "x5", "o1", "x6", "o2", "x4", "o3"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "P0 wins: vertical in column 3",
        "actions": ["x3", "o0", "x3", "o0", "x3", "o0", "x3"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: vertical in column 6",
        # P0 alternates between cols 0 and 5 (no vertical/horizontal win)
        # P1 stacks 4 in col 6
        "actions": ["x0", "o6", "x5", "o6", "x0", "o6", "x5", "o6"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Non-terminal after first move",
        "actions": ["x3"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Three-in-a-row is not terminal",
        "actions": ["x0", "o1", "x0", "o1", "x0"],
        "checks": {"terminal": False, "current_player": 1},
    },
]
