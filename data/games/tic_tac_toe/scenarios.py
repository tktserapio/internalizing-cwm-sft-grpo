"""
Scenarios for Tic-Tac-Toe (3x3).
P0 plays 'x', P1 plays 'o'.  Action format: x(row,col) or o(row,col), 0-indexed.
Win: 3 in a row (horizontal, vertical, or diagonal).
Draw: board full with no winner.
"""

SCENARIOS = [
    {
        "name": "P0 wins: top row (0,0)-(0,1)-(0,2)",
        "actions": ["x(0,0)", "o(1,0)", "x(0,1)", "o(1,1)", "x(0,2)"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P0 wins: left column (0,0)-(1,0)-(2,0)",
        "actions": ["x(0,0)", "o(0,1)", "x(1,0)", "o(0,2)", "x(2,0)"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P0 wins: main diagonal (0,0)-(1,1)-(2,2)",
        "actions": ["x(0,0)", "o(0,1)", "x(1,1)", "o(0,2)", "x(2,2)"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: middle column (0,1)-(1,1)-(2,1)",
        "actions": ["x(0,0)", "o(0,1)", "x(2,0)", "o(1,1)", "x(0,2)", "o(2,1)"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "P1 wins: anti-diagonal (0,2)-(1,1)-(2,0)",
        "actions": ["x(0,0)", "o(0,2)", "x(2,2)", "o(1,1)", "x(1,0)", "o(2,0)"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Draw: board full, no winner (cat's game)",
        "actions": [
            "x(0,0)", "o(1,1)", "x(0,1)", "o(0,2)",
            "x(2,0)", "o(1,0)", "x(1,2)", "o(2,2)", "x(2,1)",
        ],
        "checks": {"terminal": True, "rewards_sign": [0, 0]},
    },
    {
        "name": "Non-terminal after first move",
        "actions": ["x(0,0)"],
        "checks": {"terminal": False, "current_player": 1},
    },
]
