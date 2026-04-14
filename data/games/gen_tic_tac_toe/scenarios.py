"""
Scenarios for Generalized Tic-Tac-Toe (6×6 board, win = 4 in a row).
P0 places first; P1 places second.
Action format: "row,col" (0-indexed, e.g. "0,0").
Win: 4 consecutive in a row, column, or diagonal.
Draw: board full with no winner.
"""

SCENARIOS = [
    {
        "name": "P0 wins: 4 in top row (cols 0-3)",
        "actions": ["0,0", "1,0", "0,1", "1,1", "0,2", "1,2", "0,3"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P0 wins: 4 in column 0 (rows 0-3)",
        "actions": ["0,0", "0,1", "1,0", "0,2", "2,0", "0,3", "3,0"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P0 wins: 4 on main diagonal",
        "actions": ["0,0", "0,1", "1,1", "0,2", "2,2", "0,3", "3,3"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: 4 in second row (cols 0-3)",
        "actions": ["0,0", "1,0", "2,0", "1,1", "3,0", "1,2", "4,0", "1,3"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "P1 wins: 4 in column 5 (rows 2-5)",
        # P0 plays (0,0),(0,1),(0,2) then breaks the row at (1,0) — no 4-in-a-row
        "actions": ["0,0", "2,5", "0,1", "3,5", "0,2", "4,5", "1,0", "5,5"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Three-in-a-row is not yet terminal",
        "actions": ["0,0", "1,0", "0,1", "1,1", "0,2"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Non-terminal after first move",
        "actions": ["3,3"],
        "checks": {"terminal": False, "current_player": 1},
    },
]
