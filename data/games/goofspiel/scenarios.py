"""
Scenarios for Goofspiel.
Chance actions: "prize:N" (N=1-13).
Player actions: "bid:N" (N=1-13, from hand).
P0 bids first each round; higher bid wins the prize; ties discard the prize.
First player to more points after 13 rounds wins.
"""

# P0 wins all: prizes descending, P0 bids max, P1 bids min
# Round i: prize=13-i, P0 bids 13-i, P1 bids i+1
# P0 wins prizes 13,12,11,10,9,8 (rounds 0-5); tie at 7; P1 wins 6,5,4,3,2,1 (rounds 7-12)
# P0 total=63, P1 total=21 → P0 wins
_P0_WINS = []
for i in range(13):
    prize = 13 - i
    p0_bid = 13 - i
    p1_bid = i + 1
    _P0_WINS += [f"prize:{prize}", f"bid:{p0_bid}", f"bid:{p1_bid}"]

# P1 wins all: prizes descending, P0 bids min, P1 bids max
# P1 wins prizes 13,12,...,8; P0 wins 6,5,...,1; P1 total=63, P0 total=21
_P1_WINS = []
for i in range(13):
    prize = 13 - i
    p0_bid = i + 1
    p1_bid = 13 - i
    _P1_WINS += [f"prize:{prize}", f"bid:{p0_bid}", f"bid:{p1_bid}"]

SCENARIOS = [
    {
        "name": "P0 wins a round with higher bid",
        "actions": ["prize:5", "bid:7", "bid:3"],
        "checks": {"terminal": False, "current_player": -1},
    },
    {
        "name": "Tie: prize discarded, both bid same",
        "actions": ["prize:5", "bid:4", "bid:4"],
        "checks": {"terminal": False, "current_player": -1},
    },
    {
        "name": "P1 wins a round with higher bid",
        "actions": ["prize:5", "bid:2", "bid:6"],
        "checks": {"terminal": False, "current_player": -1},
    },
    {
        "name": "Non-terminal after first prize dealt",
        "actions": ["prize:7"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "P0 wins overall (bids max each round)",
        "actions": _P0_WINS,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins overall (P0 bids min each round)",
        "actions": _P1_WINS,
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
]
