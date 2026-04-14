"""
Scenarios for Hanabi (2-player cooperative, chance-dealt cards).
Chance actions: "deal:COLOR,RANK" for initial deals and mid-game draws.
Player actions: "Play N", "Discard N", "Reveal color P C", "Reveal rank P R".
P0 acts first after the 10-card deal (5 to P0, 5 to P1).
Game ends: 4 bad plays (lives<0), perfect score (25), or deck exhausted.
Rewards are cooperative: get_rewards returns [score, score] for both players.
"""

# Fixed deal: P0 gets R1,B3,G1,W5,R2; P1 gets Y1,Y1,G2,B4,W1
_DEAL = [
    "deal:R,1", "deal:B,3", "deal:G,1", "deal:W,5", "deal:R,2",  # P0
    "deal:Y,1", "deal:Y,1", "deal:G,2", "deal:B,4", "deal:W,1",  # P1
]

SCENARIOS = [
    {
        "name": "Non-terminal after first action: P0 plays, P1 to act",
        # P0 plays index 0 (R,1). Board R was 0, R1 is next → success. Board: R=1.
        # P0 needs to draw, so current_player becomes -1 (chance) for the draw.
        "actions": _DEAL + ["Play 0"],
        "checks": {"terminal": False, "current_player": -1},
    },
    {
        "name": "Non-terminal after P0 plays and draws: P1 to act",
        # P0 plays R1 (success), draws G3 from deck. Now P1's turn.
        "actions": _DEAL + ["Play 0", "deal:G,3"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Non-terminal after P0 and P1 each discard once",
        # P0 discards index 0 (R1), draws G3. P1 discards index 0 (Y1), draws R1.
        # Clues: 8→9 capped at 8, then 8→9 capped at 8. Back to P0.
        "actions": _DEAL + ["Discard 0", "deal:G,3", "Discard 0", "deal:R,1"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "Non-terminal after reveal action (no draw needed)",
        # P0 reveals rank 1 to P1 (Y1,Y1,W1 are rank 1). Clues: 8→7. P1's turn.
        "actions": _DEAL + ["Reveal rank 1 1"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Non-terminal after P0 plays wrong card (life lost)",
        # P0 plays index 1 (B,3). Board B=0, needs B1 not B3 → fail. Lives: 3→2.
        # Card goes to discard. P0 draws.
        "actions": _DEAL + ["Play 1", "deal:G,3"],
        "checks": {"terminal": False, "current_player": 1},
    },
]
