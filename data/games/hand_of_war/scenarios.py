"""
Scenarios for Hand of War (16-card deck).
Chance action: "deal:C1,C2,...,C16" (sorted deck split: P0=first 8, P1=last 8).
Player actions: "play:CARD".
Card values: A=4, K=3, Q=2, J=1. Higher card wins both cards.
Game ends when replenish fails (draw pile and hand depleted).
"""

_DEAL_DEFAULT = "deal:Ac,Ad,Ah,As,Jc,Jd,Jh,Js,Kc,Kd,Kh,Ks,Qc,Qd,Qh,Qs"
# P0 gets Aces+Jacks, P1 gets Kings+Queens

# P0 wins: Aces(4) beat Kings(3), Jacks(1) lose to Queens(2); P0 ends with 8 win-pile cards
_P0_WINS = [
    _DEAL_DEFAULT,
    "play:Ac", "play:Kc",
    "play:Ad", "play:Kd",
    "play:Ah", "play:Kh",
    "play:As", "play:Ks",
    "play:Jc", "play:Qc",
    "play:Jd", "play:Qd",
]

# P1 wins: P0 gets Jacks+Queens, P1 gets Aces+Kings; Aces beat all → P1 wins all rounds
_DEAL_P1_WINS = "deal:Jc,Jd,Jh,Js,Qc,Qd,Qh,Qs,Ac,Ad,Ah,As,Kc,Kd,Kh,Ks"
_P1_WINS = [
    _DEAL_P1_WINS,
    "play:Jc", "play:Ac",
    "play:Jd", "play:Ad",
    "play:Jh", "play:Ah",
    "play:Js", "play:As",
    "play:Qc", "play:Kc",
    "play:Qd", "play:Kd",
]

# Draw: alternating A/J for P0, K/Q for P1 → each wins alternate rounds, equal win piles
_DEAL_DRAW = "deal:Ac,Jc,Ad,Jd,Ah,Jh,As,Js,Kc,Qc,Kd,Qd,Kh,Qh,Ks,Qs"
_DRAW = [
    _DEAL_DRAW,
    "play:Ac", "play:Kc",
    "play:Jc", "play:Qc",
    "play:Ad", "play:Kd",
    "play:Jd", "play:Qd",
    "play:Ah", "play:Kh",
    "play:Jh", "play:Qh",
]

SCENARIOS = [
    {
        "name": "Non-terminal after deal: P0 acts first",
        "actions": [_DEAL_DEFAULT],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "P0 wins single battle: Ace beats King",
        "actions": [_DEAL_DEFAULT, "play:Ac", "play:Kc"],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "P0 wins overall: Aces beat Kings, Jacks lose to Queens",
        "actions": _P0_WINS,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins overall: Aces+Kings beat Jacks+Queens",
        "actions": _P1_WINS,
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Draw: alternating wins leave equal win piles",
        "actions": _DRAW,
        "checks": {"terminal": True, "rewards_sign": [0, 0]},
    },
]
