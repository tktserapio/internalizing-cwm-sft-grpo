"""
Scenarios for Havannah (board size 10).
Action format: column letter + row number (e.g., "J10" for center).
Coordinate mapping: col = chr('A' + (x+9)), row = z+10.
Corners: S1=(9,0,-9), J1=(0,9,-9), A10=(-9,9,0), A19=(-9,0,9), J19=(0,-9,9), S10=(9,-9,0).
Win conditions: Bridge (connect 2 corners), Ring (enclosed region), Fork (3+ corners).
P0 goes first.
"""

# P0 wins via Bridge: connect corners J1 and S1 along row 1 (z=-9)
# Chain: J1-K1-L1-M1-N1-O1-P1-Q1-R1-S1 (direction +x,-y)
# P1 interleaves with non-interfering moves in middle rows
_P0_BRIDGE = [
    "J1", "J11",
    "K1", "J12",
    "L1", "J13",
    "M1", "J14",
    "N1", "J15",
    "O1", "J16",
    "P1", "J17",
    "Q1", "J18",
    "R1", "K11",
    "S1",   # P0 plays S1 → chain J1..S1 connects two corners → P0 wins
]

# P1 wins via Bridge: connect corners A10 and A19 along col A (x=-9)
# Chain: A10-A11-A12-A13-A14-A15-A16-A17-A18-A19
# P0 interleaves with non-interfering moves
_P1_BRIDGE = [
    "K2", "A10",
    "K3", "A11",
    "K4", "A12",
    "K5", "A13",
    "K6", "A14",
    "K7", "A15",
    "K8", "A16",
    "K9", "A17",
    "K10", "A18",
    "K11", "A19",  # P1 plays A19 → chain A10..A19 connects two corners → P1 wins
]

SCENARIOS = [
    {
        "name": "Non-terminal after first stone placed",
        "actions": ["J10"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Non-terminal after several moves, no win yet",
        "actions": ["J10", "J11", "J12", "J9"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "P0 wins via Bridge (connects corners J1 and S1)",
        "actions": _P0_BRIDGE,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins via Bridge (connects corners A10 and A19)",
        "actions": _P1_BRIDGE,
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
]
