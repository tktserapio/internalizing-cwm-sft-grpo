"""
Scenarios for Chess (8x8 standard).
P0=White, P1=Black.
Actions: "PIECE_FROM_TO" (e.g., "P_e2_e4", "N_g1_f3", "B_f1_c4")
  PIECE: P/N/B/R/Q/K
  FROM/TO: algebraic (a-h, 1-8)
Promotion: "P_e7_e8_Q"
Castling: "O-O" (kingside) or "O-O-O" (queenside).
Draw rule: 50 consecutive half-moves without pawn move or capture.
"""

# Fool's Mate: White opens king diagonal with f3+g4; Black Qh4#  (P1 wins in 4 moves)
_FOOLS_MATE = ["P_f2_f3", "P_e7_e5", "P_g2_g4", "Q_d8_h4"]

# Scholar's Mate: 1.e4 e5 2.Bc4 Nc6 3.Qh5 Nf6 4.Qxf7# (P0 wins in 7 moves)
_SCHOLARS_MATE = [
    "P_e2_e4", "P_e7_e5",
    "B_f1_c4", "N_b8_c6",
    "Q_d1_h5", "N_g8_f6",
    "Q_h5_f7",
]

# 50-move draw: White N bounces b1↔a3, Black N bounces g8↔h6 (no pawns/captures)
_DRAW_50 = []
for _ in range(12):
    _DRAW_50 += ["N_b1_a3", "N_g8_h6", "N_a3_b1", "N_h6_g8"]
_DRAW_50 += ["N_b1_a3", "N_g8_h6"]  # moves 49-50 → halfmove_clock=50

# Kingside castle setup: clear f1+g1 for White then O-O
_CASTLE_SETUP = ["P_e2_e4", "P_d7_d6", "N_g1_f3", "P_c7_c6", "B_f1_c4", "P_b7_b6", "O-O"]

SCENARIOS = [
    {
        "name": "Non-terminal after 1.e4: P1 to move",
        "actions": ["P_e2_e4"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Fool's Mate: P1 (Black) wins in 4 moves",
        "actions": _FOOLS_MATE,
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Scholar's Mate: P0 (White) wins in 7 moves",
        "actions": _SCHOLARS_MATE,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "Draw by 50-move rule: 50 consecutive knight shuffles",
        "actions": _DRAW_50,
        "checks": {"terminal": True, "rewards_sign": [0, 0]},
    },
    {
        "name": "P0 castles kingside after clearing f1+g1",
        "actions": _CASTLE_SETUP,
        "checks": {"terminal": False, "current_player": 1},
    },
]
