"""
Scenarios for Gin Rummy.
Chance action: "deal:C1,...,C52" or "deal_random".
  deck[0:10] → P0 hand, deck[10:20] → P1 hand, deck[20] → upcard.
Player actions: "Pass", "Draw upcard", "Draw stock",
                "Action: CARD" (discard), "Action: Knock",
                "Action: MELD_STRING" (meld declaration), "Action: Done".
"""

_P0_HAND_GIN = ["Ah", "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th"]
_P1_HAND_HIGH = ["Ks", "Kd", "Kh", "Kc", "Qs", "Qd", "Qh", "Qc", "Js", "Jd"]
_UPCARD = "Jh"
_REST = ["Jc", "Ts", "Td", "Tc", "9s", "9d", "9c", "8s", "8d", "8c",
         "7s", "7d", "7c", "6s", "6d", "6c", "5s", "5d", "5c",
         "4s", "4d", "4c", "3s", "3d", "3c", "2s", "2d", "2c", "As", "Ad", "Ac"]

_DEAL_P0_GIN = "deal:" + ",".join(_P0_HAND_GIN + _P1_HAND_HIGH + [_UPCARD] + _REST)
# P0 swapped to P1: P0 gets high deadwood, P1 gets gin hand
_DEAL_P1_GIN = "deal:" + ",".join(_P1_HAND_HIGH + _P0_HAND_GIN + [_UPCARD] + _REST)
# Wall scenario: only 3 cards in rest so deck runs dry quickly
_DEAL_WALL = "deal:" + ",".join(_P0_HAND_GIN + _P1_HAND_HIGH + [_UPCARD, "Jc", "As", "Ad"])

# P0 wins gin: deal → P1 passes first turn → P0 draws upcard (Jh) → P0 knocks gin
# → declares two 5-card runs → Done → terminal
_P0_GIN_WIN = [
    _DEAL_P0_GIN,
    "Pass",             # P1 passes upcard
    "Draw upcard",      # P0 draws Jh → hand is Ah-Jh (11 cards, all hearts, 0 deadwood)
    "Action: Knock",    # P0 knocks gin (deadwood=0)
    "Action: Ah2h3h4h5h",  # P0 declares meld 1
    "Action: 6h7h8h9hTh",  # P0 declares meld 2 (Jh left over)
    "Action: Done",     # P0 done → gin: P1 gets no layoff → terminal
]

# P1 wins gin: P1 has gin hand → P1 draws upcard Jh → P1 knocks gin immediately
_P1_GIN_WIN = [
    _DEAL_P1_GIN,
    "Draw upcard",       # P1 draws Jh → P1 hand is Ah-Jh (11 cards, 0 deadwood)
    "Action: Knock",     # P1 knocks gin
    "Action: Ah2h3h4h5h",
    "Action: 6h7h8h9hTh",
    "Action: Done",
]

# Wall (draw): deck runs out → Action: Pass → game over with [0, 0]
# Both players pass upcard, P1 draws Jc, discards, P0 draws As, discards → wall
_WALL = [
    _DEAL_WALL,
    "Pass",          # P1 passes upcard
    "Pass",          # P0 passes → P1 draws Jc from stock, enters discard
    "Action: Jc",    # P1 discards Jc (deck now has As, Ad = 2 cards)
    "Draw stock",    # P0 draws As (deck now has Ad = 1 card < 2 → wall triggered)
    "Action: Ah",    # P0 discards Ah → wall phase
    "Action: Pass",  # wall pass → terminal [0, 0]
]

SCENARIOS = [
    {
        "name": "Non-terminal after deal: P1 acts first (first_turn phase)",
        "actions": [_DEAL_P0_GIN],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Non-terminal: P1 passes, P0 passes, P1 draws and discards → P0 draw phase",
        "actions": [_DEAL_P0_GIN, "Pass", "Pass", "Action: Ks"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "P0 wins gin: perfect run hand knocks immediately after drawing",
        "actions": _P0_GIN_WIN,
        "checks": {"terminal": True, "rewards_sign": [1, 0]},
    },
    {
        "name": "P1 wins gin: P1 draws upcard and knocks gin immediately",
        "actions": _P1_GIN_WIN,
        "checks": {"terminal": True, "rewards_sign": [0, 1]},
    },
    {
        "name": "Draw (wall): deck runs out → Action: Pass → game over with no winner",
        "actions": _WALL,
        "checks": {"terminal": True, "rewards_sign": [0, 0]},
    },
]
