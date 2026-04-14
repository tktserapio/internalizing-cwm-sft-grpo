"""
Scenarios for Blackjack (single-player vs dealer).
Chance actions: "deal:CARD" (4 initial deals: p1, d1, p2, d2; then on hit).
Player (P0) actions: "H" (hit), "S" (stand), "D" (double), "R" (surrender), "P" (split).
Dealer (P1) actions: "H" (if <17), "S" (if >=17, then resolve).
Deal order: P0 card1, dealer card1, P0 card2, dealer card2.
"""

SCENARIOS = [
    {
        "name": "Non-terminal after initial 4 deals: P0 acts",
        "actions": ["deal:5h", "deal:2s", "deal:9c", "deal:Kd"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "Player busts: hit 9+8=17 then King → 27",
        "actions": ["deal:9h", "deal:2s", "deal:8c", "deal:Kd", "H", "deal:Ks"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Dealer busts: P0 stands 20, dealer 12 hits to 22",
        "actions": ["deal:Kh", "deal:7s", "deal:Ts", "deal:5d", "S", "H", "deal:Qh", "S"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "Natural blackjack (Ace+King): P0 wins 1.5x",
        "actions": ["deal:Ah", "deal:5s", "deal:Ks", "deal:7d", "S", "H", "deal:Qc", "S"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P0 surrenders: immediate -0.5 loss",
        "actions": ["deal:5h", "deal:Kd", "deal:6c", "deal:9s", "R"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Dealer wins: P0 stands at 17, dealer has 20",
        "actions": ["deal:Jh", "deal:Ks", "deal:7d", "deal:Td", "S", "S"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
]
