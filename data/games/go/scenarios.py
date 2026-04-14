"""
Scenarios for Go (9x9 board, komi=6.5 for White/P1).
Player actions: "place_R_C" or "pass".
P0=Black, P1=White. Two consecutive passes end the game.
Scoring: area scoring (stones + enclosed territory) + komi for P1.
"""

# P0 (Black) wins: fills rows 0-4 (45 cells), P1 fills rows 5-8 (36 cells),
# P1 passes 9 times while P0 finishes, then both pass to end.
# Score: P0=45, P1=36+6.5=42.5 → P0 wins.
_p0_moves = [f"place_{r}_{c}" for r in range(5) for c in range(9)]  # 45 moves
_p1_moves = [f"place_{r}_{c}" for r in range(5, 9) for c in range(9)]  # 36 moves
_P0_WINS = []
for i in range(36):
    _P0_WINS.append(_p0_moves[i])
    _P0_WINS.append(_p1_moves[i])
for i in range(36, 45):
    _P0_WINS.append(_p0_moves[i])
    _P0_WINS.append("pass")
_P0_WINS += ["pass", "pass"]

SCENARIOS = [
    {
        "name": "Non-terminal after first stone placed",
        "actions": ["place_0_0"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Two passes end game: P1 wins on empty board (komi advantage)",
        "actions": ["pass", "pass"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Capture: P0 surrounds P1 stone at (1,0) → P1's stone removed",
        "actions": ["place_0_0", "place_1_0", "place_2_0", "place_5_5", "place_1_1"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Non-terminal after several moves, no passes",
        "actions": ["place_4_4", "place_4_5", "place_3_4", "place_5_5"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "P0 wins: fills top 5 rows (45 pts) vs P1 bottom 4 rows (36+6.5=42.5 pts)",
        "actions": _P0_WINS,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
]
