"""
Scenarios for Checkers (8x8).
P0=Red (moves up, rows 5-7 initially), P1=Black (moves down, rows 0-2 initially).
Actions: "move_SR_SC_ER_EC" (simple move) or "jump_R0_C0_R1_C1_..." (capture chain).
Jumps are mandatory when available.
Draw: 40 consecutive non-capture moves.
"""

# Setup: P0 at (5,2)→(4,3); P1 at (2,3)→(3,4) walks into capture range.
# P0 now has mandatory jump: jump_4_3_2_1 (captures P1 piece at (3,4)).
_JUMP_SETUP = ["move_5_2_4_3", "move_2_3_3_4"]

SCENARIOS = [
    {
        "name": "Non-terminal after P0's first move",
        "actions": ["move_5_0_4_1"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Non-terminal after two alternating simple moves",
        "actions": ["move_5_0_4_1", "move_2_1_3_0"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "Mandatory jump setup: only jump in legal actions",
        "actions": _JUMP_SETUP,
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "P0 executes mandatory jump: captures P1 piece at (3,4)",
        "actions": _JUMP_SETUP + ["jump_4_3_2_1"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Non-terminal after four alternating moves",
        "actions": ["move_5_4_4_5", "move_2_5_3_4", "move_5_6_4_7", "move_2_7_3_6"],
        "checks": {"terminal": False, "current_player": 0},
    },
]
