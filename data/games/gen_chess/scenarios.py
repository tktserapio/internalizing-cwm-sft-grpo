"""
Scenarios for Gen Chess (5x5 board, otherwise standard chess rules, no castling).
P0=White, P1=Black.
Files a-e (cols 0-4), Ranks 1-5 (rows 0-4).
White: R(a1),N(b1),B(c1),Q(d1),K(e1), pawns at rank 2.
Black: r(a5),n(b5),b(c5),q(d5),k(e5), pawns at rank 4.
Actions: "PIECE_FROM_TO" (e.g., "P_a2_a3", "N_b1_a3") or promotion "P_e4_e5_Q".
Draw rule: 100 consecutive half-moves without pawn move or capture.
"""

# P0 wins: N captures c4 pawn giving check, Black king walks to e4, P_d2_d3 checkmates
_P0_WIN = ["N_b1_a3", "P_e4_e3", "N_a3_c4", "K_e5_e4", "P_d2_d3"]

# P1 wins: Black N captures White N on a3, White king walks to e2, Black P_d4_d3 checkmates
_P1_WIN = ["N_b1_a3", "N_b5_a3", "P_e2_e3", "N_a3_c2", "K_e1_e2", "P_d4_d3"]

# Draw by 100 halfmoves: White N bounces b1↔a3, Black N bounces b5↔c3 (no captures)
_DRAW_100 = []
for _ in range(25):
    _DRAW_100 += ["N_b1_a3", "N_b5_c3", "N_a3_b1", "N_c3_b5"]

SCENARIOS = [
    {
        "name": "Non-terminal after first move: P1 to move",
        "actions": ["P_a2_a3"],
        "checks": {"terminal": False, "current_player": 1},
    },
    {
        "name": "Non-terminal after 4 moves: P0 to move",
        "actions": _P0_WIN[:4],
        "checks": {"terminal": False, "current_player": 0},
    },
    {
        "name": "P0 wins: knight fork forces king to e4, pawn delivers checkmate",
        "actions": _P0_WIN,
        "checks": {"terminal": True, "rewards_sign": [1, -1]},
    },
    {
        "name": "P1 wins: Black N infiltrates to c2, pawn advance checkmates White king",
        "actions": _P1_WIN,
        "checks": {"terminal": True, "rewards_sign": [-1, 1]},
    },
    {
        "name": "Draw by 100-move rule: 100 knight shuffles without pawn or capture",
        "actions": _DRAW_100,
        "checks": {"terminal": True, "rewards_sign": [0, 0]},
    },
]
