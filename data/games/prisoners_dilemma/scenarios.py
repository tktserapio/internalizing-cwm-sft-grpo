"""
Scenarios for Prisoner's Dilemma.
Payoff matrix (P0, P1): C/C=(3,3), C/D=(0,5), D/C=(5,0), D/D=(1,1).
Rewards normalised to zero-sum by subtracting the mean of the two payoffs:
  C/D → (-2.5, +2.5), D/C → (+2.5, -2.5), C/C and D/D → (0, 0).
"""

SCENARIOS = [
    {
        "name": "P1 benefits: P0 cooperates, P1 defects",
        "actions": ["C", "D"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "P0 benefits: P0 defects, P1 cooperates",
        "actions": ["D", "C"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "Mutual cooperation: equal payoff",
        "actions": ["C", "C"],
        "checks": {"terminal": True, "rewards_sign": [0, 0]},
    },
    {
        "name": "Mutual defection: equal payoff",
        "actions": ["D", "D"],
        "checks": {"terminal": True, "rewards_sign": [0, 0]},
    },
    {
        "name": "Non-terminal after P0 moves",
        "actions": ["D"],
        "checks": {"terminal": False, "current_player": 1},
    },
]
