CURRICULUM = [
    # Tier 1
    ["tic_tac_toe", "connect4", "matching_pennies", "prisoners_dilemma", "pig", "dots_and_boxes"],
    # Tier 2
    ["blackjack", "kuhn_poker", "go", "breakthrough", "first_price_auction", "pentago"],
    # Tier 3
    ["liars_dice", "goofspiel", "battleship", "checkers", "chess", "leduc_poker"],
    # Tier 4
    ["havannah", "negotiation", "poker_holdem", "backgammon", "hanabi"],
]

TRAINING_GAMES = [game for tier in CURRICULUM for game in tier]

EVAL_GAMES = [
    # perfect
    "y",
    "gen_tic_tac_toe", # OOD
    "gen_chess", # OOD
    "converge", # OOD
    # imperfect
    "gin_rummy",
    "quadranto", # OOD
    "hand_of_war" # OOD
]

IMPERFECT_INFO_GAMES = {
    "kuhn_poker", "leduc_poker", "blackjack", "liars_dice",
    "goofspiel", "hand_of_war", "quadranto", "gin_rummy", "poker_holdem",
    "matching_pennies", "prisoners_dilemma", "first_price_auction",
    "negotiation", "battleship", "hanabi"
}

TIER_WEIGHTS = {
    "static": 0.15,
    "dynamics": 0.25,
    "information": 0.30,
    "scenarios": 0.30,
}


def get_info_type(game: str) -> str:
    """Return 'imperfect' or 'perfect' for a game."""
    return "imperfect" if game in IMPERFECT_INFO_GAMES else "perfect"


def validate_curriculum():
    """Check that curriculum games don't overlap with eval games."""
    training_set = set(TRAINING_GAMES)
    eval_set = set(EVAL_GAMES)
    overlap = training_set & eval_set
    if overlap:
        raise ValueError(f"Games in both training and eval: {overlap}")
    return True