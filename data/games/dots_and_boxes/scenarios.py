"""
Scenarios for Dots and Boxes (3x3 dots = 2x2 boxes).
Horizontal edges: "h_r_c" (between dots (r,c) and (r,c+1)).
Vertical edges: "v_r_c" (between dots (r,c) and (r+1,c)).
Completing the 4th side of a box scores 1 point and grants an extra turn.
Most boxes at end wins; equal boxes is a draw.
"""

# P0 wins 4-0: set up all 4 boxes with 3 sides, then P0 completes both chains
# After setup (10 moves), P0 plays v_0_1 (completes boxes 0,0 and 0,1) then v_1_1
_P0_WIN = [
    "h_0_0", "h_0_1", "h_1_0", "h_1_1",
    "h_2_0", "h_2_1", "v_0_0", "v_0_2",
    "v_1_0", "v_1_2",  # P1's last setup
    "v_0_1",            # P0 completes top chain (boxes 0,0 and 0,1), keeps turn
    "v_1_1",            # P0 completes bottom chain (boxes 1,0 and 1,1)
]

# P1 wins 4-0: v_0_1 drawn early by P0 (no box yet), P1 completes chains
_P1_WIN = [
    "v_0_1", "h_0_0",   # P0 draws v_0_1 (only 1 of 4 for any box), P1 draws h_0_0
    "h_1_0", "v_0_0",   # P1 plays v_0_0 → box(0,0) completes! P1 scores, keeps turn
    "h_0_1", "h_1_1",   # P1 draws h_0_1; P0 draws h_1_1
    "v_0_2",            # P1 plays v_0_2 → box(0,1) completes! P1 scores, keeps turn
    "h_2_0", "v_1_0",   # P1 draws h_2_0; P0 draws v_1_0
    "h_2_1", "v_1_2",   # P1 draws h_2_1; P0 draws v_1_2
    "v_1_1",            # P1 plays v_1_1 → boxes(1,0) and (1,1) complete! P1 scores
]

# Draw 2-2: P0 scores top chain (boxes 0,0+0,1), P1 scores bottom chain (boxes 1,0+1,1)
# Key: v_1_1 is drawn early (step 4 by P1) so box(1,0) completes when v_1_0 is drawn later
_DRAW = [
    "h_0_0", "h_0_1", "v_0_0", "v_1_1",   # v_1_1 early (no box yet)
    "h_1_0", "h_1_1", "v_0_2", "h_2_0",   # setup
    "v_0_1",                                # P0 completes boxes(0,0) and (0,1), keeps turn
    "h_2_1",                                # P0 plays h_2_1 (setup for box 1,1); P1's turn
    "v_1_0",                                # P1 plays v_1_0 → box(1,0) completes! P1 scores, keeps turn
    "v_1_2",                                # P1 plays v_1_2 → box(1,1) completes! P1 scores
]

SCENARIOS = [
    {
        "name": "Non-terminal after first edge",
        "actions": ["h_0_0"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "P0 completes a box and keeps the turn",
        "actions": ["h_0_0", "h_1_0", "v_0_0", "h_2_0", "v_0_1"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "P0 wins 4-0: captures both chains",
        "actions": _P0_WIN,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins 4-0: captures both chains",
        "actions": _P1_WIN,
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Draw 2-2: P0 and P1 each capture one chain",
        "actions": _DRAW,
        "checks": {"terminal": True, "rewards_sign": [0, 0]},
    },
]
