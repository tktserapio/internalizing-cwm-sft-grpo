"""
Scenarios for Leduc Poker.
Deck: J, J, Q, Q, K, K (two of each rank).
Ranks: K > Q > J.  Pair (private matches public) beats any non-pair.
Pot starts at SB=1 + BB=2 = 3.
Chance actions: "deal:J", "deal:Q", "deal:K".
Player actions: "Fold", "Call", "Raise".
Deal order: P0 private card, then P1 private card, then after round-1 betting
the public (board) card.
"""

SCENARIOS = [
    {
        "name": "P0 folds preflop: P1 wins the pot",
        "actions": ["deal:K", "deal:Q", "Fold"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "P1 folds after P0 raises first: P0 wins",
        # P0 (SB) raises; P1 (BB) folds → P0 collects the pot
        "actions": ["deal:K", "deal:Q", "Raise", "Fold"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "Showdown: K beats J (both check both rounds)",
        "actions": ["deal:K", "deal:J", "Call", "Call", "deal:Q", "Call", "Call"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "Showdown: J loses to K (both check both rounds)",
        "actions": ["deal:J", "deal:K", "Call", "Call", "deal:Q", "Call", "Call"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Showdown: K beats Q (both check both rounds)",
        "actions": ["deal:K", "deal:Q", "Call", "Call", "deal:J", "Call", "Call"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "Pair beats non-pair: P0 has K + public K",
        "actions": ["deal:K", "deal:J", "Call", "Call", "deal:K", "Call", "Call"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P0 folds postflop facing P1 raise: P1 wins",
        # Preflop: both call/check.  Postflop: P0 checks (Call), P1 raises, P0 folds → P1 wins
        "actions": ["deal:K", "deal:Q", "Call", "Call", "deal:J", "Call", "Raise", "Fold"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Non-terminal after preflop deal",
        "actions": ["deal:K", "deal:Q"],
        "checks": {"terminal": False, "current_player": 0},
    },
]
