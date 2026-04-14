"""
Scenarios for Kuhn Poker.
Cards K > Q > J.  Chance action = 2-char string: first char = P0's card,
second char = P1's card (e.g. "KJ" means P0 has K, P1 has J).
Player actions: Fold, Call, Raise.
Pot starts at ante=1 each.  Raise adds 1 more.
Payoffs:
  Call-end: winner gets +1, loser -1.
  Raise-end: winner gets +2, loser -2.
"""

SCENARIOS = [
    {
        "name": "P0 wins at showdown: K beats J (Call-Call)",
        "actions": ["KJ", "Call", "Call"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins at showdown: K beats J (Call-Call, P0 has J)",
        "actions": ["JK", "Call", "Call"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "P0 wins: P1 folds after P0 raises",
        "actions": ["KJ", "Raise", "Fold"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: P0 folds after P1 re-raises",
        "actions": ["QK", "Call", "Raise", "Fold"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "P0 wins raised pot: K beats J (Raise-Call showdown)",
        "actions": ["KJ", "Raise", "Call"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P0 wins raised pot: K beats Q (Call-Raise-Call showdown)",
        "actions": ["KQ", "Call", "Raise", "Call"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "Non-terminal after chance deal",
        "actions": ["KJ"],
        "checks": {"terminal": False, "current_player": 0},
    },
]
