"""
Scenarios for First-Price Sealed-Bid Auction.
Chance action: 2-digit string "V0V1" where V0 = P0's private valuation (1-5),
V1 = P1's private valuation (1-5).
Player actions: "bid_0" through "bid_5".
Highest bid wins; ties go to P0.
Winner's reward = (valuation - winning_bid) / 2; loser pays the symmetric cost.
"""

SCENARIOS = [
    {
        "name": "P0 wins: P0 bids higher than P1",
        "actions": ["31", "bid_2", "bid_1"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: P1 bids higher than P0",
        "actions": ["13", "bid_0", "bid_2"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "P0 wins tie-break: equal bids go to P0",
        "actions": ["33", "bid_2", "bid_2"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P0 wins with high valuation and high bid",
        "actions": ["53", "bid_4", "bid_1"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins with higher bid on high valuation",
        "actions": ["15", "bid_0", "bid_4"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Non-terminal after chance deal",
        "actions": ["33"],
        "checks": {"terminal": False, "current_player": 0},
    },
]
