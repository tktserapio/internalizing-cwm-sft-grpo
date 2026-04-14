"""
Scenarios for Texas Hold'em Poker (Limit, 2-player).
Chance actions: "deal:RANKSUIT" (e.g., "deal:Ac").
Deal order: P0 hole1, P0 hole2, P1 hole1, P1 hole2, then board.
Player actions: "Fold", "Call", "Check", "Raise".
P0 is Small Blind (1), P1 is Big Blind (2).
Preflop: P0 acts first (needs to call 1 more or fold/raise).
Post-flop: P1 acts first.
"""

# Full sequence: P0 Ace-high beats P1 low-high at showdown (both check through)
_P0_SHOWDOWN_WIN = [
    # Hole cards: P0 gets Ac,Kc; P1 gets 2d,3d
    "deal:Ac", "deal:Kc", "deal:2d", "deal:3d",
    # Preflop: P0 calls SB (1→2), P1 checks (already BB=2) → advance to flop
    "Call", "Check",
    # Flop: 5h, 7s, 9c
    "deal:5h", "deal:7s", "deal:9c",
    # Flop betting: P1 checks, P0 checks → advance to turn
    "Check", "Check",
    # Turn: Jd
    "deal:Jd",
    # Turn betting: P1 checks, P0 checks
    "Check", "Check",
    # River: Qh
    "deal:Qh",
    # River betting: P1 checks, P0 checks → showdown
    "Check", "Check",
    # P0 has AcKc+5h7s9cJdQh: best 5 = AcKcQhJd9c (high card A)
    # P1 has 2d3d+5h7s9cJdQh: best 5 = QhJd9c7s5h (high card Q)
    # P0 wins
]

SCENARIOS = [
    {
        "name": "Non-terminal after hole card deals",
        "actions": ["deal:Ac", "deal:Kc", "deal:2d", "deal:3d"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "P0 folds preflop: P1 wins pot",
        "actions": ["deal:Ac", "deal:Kc", "deal:2d", "deal:3d", "Fold"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "P1 folds after P0 calls then P1 folds: P0 wins",
        "actions": ["deal:Ac", "deal:Kc", "deal:2d", "deal:3d", "Call", "Fold"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P0 wins at showdown: Ace-high beats Queen-high",
        "actions": _P0_SHOWDOWN_WIN,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "Non-terminal after preflop Call (waiting for P1 response)",
        "actions": ["deal:Ac", "deal:Kc", "deal:2d", "deal:3d", "Call"],
        "checks": {"terminal": False, "current_player": 1},
    },
]
