"""
Scenarios for Breakthrough (8x8 board).
P0 (White) starts rows 1-2, wins by reaching row 8.
P1 (Black) starts rows 7-8, wins by reaching row 1.
Move actions: "src-dst" (forward or diagonal to empty).
Capture actions: "srcxdst" (diagonal capture of opponent).
Notation: column letter (a-h) + row number (1-8), e.g. "a2".
"""

# P0 wins: White piece on column a marches from a2 to a8 (6 forward moves)
# P1 moves column h pieces down without interfering
_P0_WIN = [
    "a2-a3", "h7-h6",
    "a3-a4", "h6-h5",
    "a4-a5", "h5-h4",
    "a5-a6", "h4-h3",
    "a6-a7", "h3-h2",
    "a7-a8",  # White reaches row 8 → P0 wins
]

# P1 wins: Black piece on column h marches from h7 to h1 (6 forward moves)
# P0 moves column a pieces up without interfering
_P1_WIN = [
    "a2-a3", "h7-h6",
    "a3-a4", "h6-h5",
    "a4-a5", "h5-h4",
    "a5-a6", "h4-h3",
    "a6-a7", "h3-h2",
    "b2-b3", "h2-h1",  # Black reaches row 1 → P1 wins
]

SCENARIOS = [
    {
        "name": "P0 single forward move is non-terminal",
        "actions": ["a2-a3"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "P0 diagonal move to empty square is non-terminal",
        "actions": ["a2-b3"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Alternating moves, not terminal after 4 plies",
        "actions": ["a2-a3", "a7-a6", "b2-b3", "b7-b6"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "P0 wins: White reaches row 8",
        "actions": _P0_WIN,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: Black reaches row 1",
        "actions": _P1_WIN,
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
]
