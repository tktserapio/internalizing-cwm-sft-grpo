"""
Scenarios for Liar's Dice.
Each player rolls 3 dice (NUM_DICE=3, SIDES=6).  1s are wild.
Chance actions: "roll:N" (N=1-6), repeated NUM_DICE times for each player
in dice_queue order [P0, P0, P0, P1, P1, P1].
Player actions: "bid:Q:F" (quantity Q of face F) or "liar" (challenge).
Challenge: if actual count of face F (including wilds) < Q → challenger wins;
           if actual count >= Q → bidder wins.
"""

SCENARIOS = [
    {
        "name": "P1 wins valid challenge: actual count < bid quantity",
        # P0 dice: 2,2,2 (no wild 1s)  P1 dice: 3,3,3
        # P0 bids bid:5:2 (5 twos) — actual twos = 3 (P0 has three 2s, no wilds) < 5
        # P1 challenges → P1 wins
        "actions": ["roll:2", "roll:2", "roll:2", "roll:3", "roll:3", "roll:3",
                    "bid:5:2", "liar"],
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "P0 wins failed challenge: actual count >= bid quantity",
        # P0 dice: 2,2,2  P1 dice: 2,2,2 — actual 2s = 6 (no wilds)
        # P0 bids bid:3:2 (3 twos) — actual = 6 >= 3 → P0 (bidder) wins
        "actions": ["roll:2", "roll:2", "roll:2", "roll:2", "roll:2", "roll:2",
                    "bid:3:2", "liar"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "Wild 1s count: challenge fails because wilds push count over bid",
        # P0 dice: 1,1,1 (all wild)  P1 dice: 6,6,6
        # P0 bids bid:3:6 (3 sixes) — actual sixes = 3 (P1's 6s) + 3 (wilds) = 6 >= 3
        # P1 challenges → fails → P0 wins
        "actions": ["roll:1", "roll:1", "roll:1", "roll:6", "roll:6", "roll:6",
                    "bid:3:6", "liar"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P0 wins: P1 challenges exact-count bid that holds",
        # P0 dice: 4,4,4  P1 dice: 5,5,5 — actual 4s = 3, bid:3:4 → 3 >= 3 → P0 wins
        "actions": ["roll:4", "roll:4", "roll:4", "roll:5", "roll:5", "roll:5",
                    "bid:3:4", "liar"],
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "Non-terminal after first bid",
        "actions": ["roll:3", "roll:3", "roll:3", "roll:4", "roll:4", "roll:4",
                    "bid:1:3"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Opening bid bid:1:1 is legal (minimum valid bid)",
        # Just verify the state is non-terminal after rolling and bidding minimum
        "actions": ["roll:2", "roll:3", "roll:4", "roll:5", "roll:6", "roll:2",
                    "bid:1:1"],
        "checks": {"terminal": False, "current_player": 1},
    },
]
