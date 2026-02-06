CURRICULUM = [
    ["tic_tac_toe", "connect4", "pig", "dots_and_boxes"],
    ["blackjack", "kuhn_poker", "go", "breakthrough", "first_price_auction", "pentago", "matching_pennies", "prisoners_dilemma"],
    ["liars_dice", "goofspiel", "battleship", "checkers", "chess", "hanabi"],
    ["havannah", "hand_of_war", "negotiation", "backgammon", "gin_rummy", "gen_chess"],
]

TRAINING_GAMES = [game for tier in CURRICULUM for game in tier]

EVAL_GAMES = [
    "gen_tic_tac_toe",
    "y",
    "leduc_poker",
    "quadranto",
    "poker_holdem", 
]

IMPERFECT_INFO_GAMES = {
    "kuhn_poker", "leduc_poker", "blackjack", "liars_dice",
    "goofspiel", "hand_of_war", "quadranto", "gin_rummy", "poker_holdem",
    "matching_pennies", "prisoners_dilemma", "first_price_auction",
    "negotiation", "battleship", "hanabi"
    
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
