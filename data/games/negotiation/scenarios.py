"""
Scenarios for Negotiation.
Items: books=2, hats=2, balls=2.
Chance action: "v0_B_H_L_v1_B_H_L" (valuations for each player).
Player actions: "propose_B_H_L" (proposer takes B books, H hats, L balls),
                "accept", "reject".
Rewards are zero-sum normalized: (my_value - mean) / 1.
"""

SCENARIOS = [
    {
        "name": "Non-terminal after valuations dealt",
        "actions": ["v0_2_1_0_v1_0_1_2", "propose_1_1_0"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "P0 wins: P0 takes all high-value items, P1 accepts",
        # P0 values books at 3, P1 values nothing → P0 reward > P1 reward
        "actions": ["v0_3_0_0_v1_0_3_0", "propose_2_2_0", "accept"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: P0 proposes to give everything to P1, P1 accepts",
        # P1 values all items at 3, P0 values nothing
        "actions": ["v0_0_0_0_v1_3_3_3", "propose_0_0_0", "accept"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Immediate rejection ends game with no deal",
        "actions": ["v0_2_2_2_v1_2_2_2", "propose_2_2_2", "reject"],
        "checks": {"terminal": True, "rewards_sign": [0, 0]},
    },
    {
        "name": "Max rounds (10 proposals) forces rejection and draw",
        "actions": (
            ["v0_2_2_2_v1_2_2_2"]
            + ["propose_1_1_1", "propose_1_1_1"] * 5
        ),
        "checks": {"terminal": True, "rewards_sign": [0, 0]},
    },
]
