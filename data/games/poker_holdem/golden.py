import random
from typing import Any, Dict, List, Optional, Tuple
from itertools import combinations

Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
NUM_PLAYERS = 2
CHANCE_PLAYER = -1
TERMINAL_PLAYER = -4

# Card representation
SUITS = ['c', 'd', 'h', 's']  # clubs, diamonds, hearts, spades
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
RANK_VALUES = {r: i for i, r in enumerate(RANKS)}

# Betting
SMALL_BLIND = 1
BIG_BLIND = 2
BET_SIZE = 2  # Fixed bet size for limit poker

# Game phases
PHASE_DEAL_HOLE = 0
PHASE_PREFLOP = 1
PHASE_DEAL_FLOP = 2
PHASE_FLOP = 3
PHASE_DEAL_TURN = 4
PHASE_TURN = 5
PHASE_DEAL_RIVER = 6
PHASE_RIVER = 7
PHASE_SHOWDOWN = 8


def _create_deck() -> List[str]:
    """Create a standard 52-card deck."""
    return [r + s for s in SUITS for r in RANKS]


def _card_to_tuple(card: str) -> Tuple[int, int]:
    """Convert card string to (rank_value, suit_index)."""
    rank, suit = card[0], card[1]
    return RANK_VALUES[rank], SUITS.index(suit)


def _evaluate_hand(cards: List[str]) -> Tuple[int, List[int]]:
    """
    Evaluate a 5-card poker hand.
    Returns (hand_rank, tiebreakers) where higher is better.
    Hand ranks: 0=high card, 1=pair, 2=two pair, 3=trips, 4=straight,
                5=flush, 6=full house, 7=quads, 8=straight flush, 9=royal flush
    """
    if len(cards) < 5:
        return (0, [0])

    ranks = sorted([RANK_VALUES[c[0]] for c in cards], reverse=True)
    suits = [c[1] for c in cards]

    is_flush = len(set(suits)) == 1

    # Check straight
    unique_ranks = sorted(set(ranks), reverse=True)
    is_straight = False
    straight_high = 0
    if len(unique_ranks) >= 5:
        for i in range(len(unique_ranks) - 4):
            if unique_ranks[i] - unique_ranks[i + 4] == 4:
                is_straight = True
                straight_high = unique_ranks[i]
                break
        # Check wheel (A-2-3-4-5)
        if set([12, 0, 1, 2, 3]).issubset(set(ranks)):
            is_straight = True
            straight_high = 3  # 5-high straight

    # Count ranks
    rank_counts = {}
    for r in ranks:
        rank_counts[r] = rank_counts.get(r, 0) + 1

    counts = sorted(rank_counts.values(), reverse=True)
    count_ranks = sorted(rank_counts.keys(), key=lambda r: (rank_counts[r], r), reverse=True)

    # Determine hand type
    if is_straight and is_flush:
        if straight_high == 12:  # Ace-high
            return (9, [straight_high])  # Royal flush
        return (8, [straight_high])  # Straight flush
    if counts == [4, 1]:
        return (7, count_ranks)  # Four of a kind
    if counts == [3, 2]:
        return (6, count_ranks)  # Full house
    if is_flush:
        return (5, ranks)  # Flush
    if is_straight:
        return (4, [straight_high])  # Straight
    if counts == [3, 1, 1]:
        return (3, count_ranks)  # Three of a kind
    if counts == [2, 2, 1]:
        return (2, count_ranks)  # Two pair
    if counts == [2, 1, 1, 1]:
        return (1, count_ranks)  # One pair
    return (0, ranks)  # High card


def _best_five_card_hand(hole: List[str], board: List[str]) -> Tuple[int, List[int]]:
    """Find the best 5-card hand from hole cards + board."""
    all_cards = hole + board
    if len(all_cards) < 5:
        return (0, [0])

    best = None
    for combo in combinations(all_cards, 5):
        score = _evaluate_hand(list(combo))
        if best is None or score > best:
            best = score
    return best


def get_initial_state() -> State:
    """Returns the initial game state."""
    return {
        "deck": _create_deck(),
        "hole_cards": [[], []],  # [P0_cards, P1_cards]
        "board": [],
        "phase": PHASE_DEAL_HOLE,
        "current_player": CHANCE_PLAYER,
        "pot": SMALL_BLIND + BIG_BLIND,
        "bets": [SMALL_BLIND, BIG_BLIND],  # P0=SB, P1=BB
        "stacks": [100 - SMALL_BLIND, 100 - BIG_BLIND],  # Starting stacks
        "to_call": BIG_BLIND - SMALL_BLIND,  # How much P0 needs to call
        "last_raiser": 1,  # BB is technically the last "raiser"
        "actions_this_round": 0,
        "folded": [False, False],
        "history": [],
        "terminal": False,
        "winner": None
    }


def _next_dealing_action(state: State) -> List[str]:
    """Get legal dealing actions for chance node."""
    deck = state["deck"]
    phase = state["phase"]

    if phase == PHASE_DEAL_HOLE:
        # Deal hole cards one at a time
        total_dealt = len(state["hole_cards"][0]) + len(state["hole_cards"][1])
        if total_dealt < 4:
            return [f"deal:{c}" for c in deck]

    elif phase == PHASE_DEAL_FLOP:
        if len(state["board"]) < 3:
            return [f"deal:{c}" for c in deck]

    elif phase == PHASE_DEAL_TURN:
        if len(state["board"]) < 4:
            return [f"deal:{c}" for c in deck]

    elif phase == PHASE_DEAL_RIVER:
        if len(state["board"]) < 5:
            return [f"deal:{c}" for c in deck]

    return []


def _betting_actions(state: State) -> List[str]:
    """Get legal betting actions for current player."""
    player = state["current_player"]
    to_call = state["to_call"] if player == 0 else 0

    # Recalculate to_call based on bets
    max_bet = max(state["bets"])
    my_bet = state["bets"][player]
    to_call = max_bet - my_bet

    actions = []

    if to_call > 0:
        actions.append("F")  # Fold
        actions.append("C")  # Call
        if state["stacks"][player] > to_call:
            actions.append("R")  # Raise
    else:
        actions.append("K")  # Check
        if state["stacks"][player] > 0:
            actions.append("R")  # Bet/Raise

    return actions


def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state."""
    if state["terminal"]:
        return []

    if state["current_player"] == CHANCE_PLAYER:
        return _next_dealing_action(state)

    return _betting_actions(state)


def _advance_phase(state: State) -> State:
    """Advance to next phase after betting round completes."""
    phase = state["phase"]

    if phase == PHASE_PREFLOP:
        state["phase"] = PHASE_DEAL_FLOP
        state["current_player"] = CHANCE_PLAYER
    elif phase == PHASE_FLOP:
        state["phase"] = PHASE_DEAL_TURN
        state["current_player"] = CHANCE_PLAYER
    elif phase == PHASE_TURN:
        state["phase"] = PHASE_DEAL_RIVER
        state["current_player"] = CHANCE_PLAYER
    elif phase == PHASE_RIVER:
        state["phase"] = PHASE_SHOWDOWN
        state["current_player"] = TERMINAL_PLAYER
        state["terminal"] = True
        # Determine winner
        hand0 = _best_five_card_hand(state["hole_cards"][0], state["board"])
        hand1 = _best_five_card_hand(state["hole_cards"][1], state["board"])
        if hand0 > hand1:
            state["winner"] = 0
        elif hand1 > hand0:
            state["winner"] = 1
        else:
            state["winner"] = -1  # Tie

    # Reset for new betting round
    state["actions_this_round"] = 0
    state["to_call"] = 0
    state["last_raiser"] = -1

    return state


def apply_action(state: State, action: Action) -> State:
    """Apply action and return new state."""
    # Deep copy
    new_state = {
        "deck": list(state["deck"]),
        "hole_cards": [list(h) for h in state["hole_cards"]],
        "board": list(state["board"]),
        "phase": state["phase"],
        "current_player": state["current_player"],
        "pot": state["pot"],
        "bets": list(state["bets"]),
        "stacks": list(state["stacks"]),
        "to_call": state["to_call"],
        "last_raiser": state["last_raiser"],
        "actions_this_round": state["actions_this_round"],
        "folded": list(state["folded"]),
        "history": state["history"] + [action],
        "terminal": False,
        "winner": None
    }

    # Handle chance actions (dealing)
    if action.startswith("deal:"):
        card = action.split(":")[1]
        new_state["deck"].remove(card)

        phase = new_state["phase"]
        if phase == PHASE_DEAL_HOLE:
            # Deal to players alternately: P0, P0, P1, P1
            total = len(new_state["hole_cards"][0]) + len(new_state["hole_cards"][1])
            player = 0 if total < 2 else 1
            new_state["hole_cards"][player].append(card)

            # Check if done dealing hole cards
            if len(new_state["hole_cards"][0]) == 2 and len(new_state["hole_cards"][1]) == 2:
                new_state["phase"] = PHASE_PREFLOP
                new_state["current_player"] = 0  # SB acts first preflop

        elif phase in [PHASE_DEAL_FLOP, PHASE_DEAL_TURN, PHASE_DEAL_RIVER]:
            new_state["board"].append(card)

            # Check if done with this dealing phase
            if phase == PHASE_DEAL_FLOP and len(new_state["board"]) == 3:
                new_state["phase"] = PHASE_FLOP
                new_state["current_player"] = 1  # BB acts first post-flop
            elif phase == PHASE_DEAL_TURN and len(new_state["board"]) == 4:
                new_state["phase"] = PHASE_TURN
                new_state["current_player"] = 1
            elif phase == PHASE_DEAL_RIVER and len(new_state["board"]) == 5:
                new_state["phase"] = PHASE_RIVER
                new_state["current_player"] = 1

        return new_state

    # Handle player actions
    player = state["current_player"]
    opponent = 1 - player

    if action == "F":
        # Fold - opponent wins
        new_state["folded"][player] = True
        new_state["terminal"] = True
        new_state["winner"] = opponent
        new_state["current_player"] = TERMINAL_PLAYER

    elif action == "C":
        # Call
        max_bet = max(new_state["bets"])
        call_amount = max_bet - new_state["bets"][player]
        call_amount = min(call_amount, new_state["stacks"][player])
        new_state["bets"][player] += call_amount
        new_state["stacks"][player] -= call_amount
        new_state["pot"] += call_amount
        new_state["actions_this_round"] += 1

        # Check if betting round ends
        if new_state["actions_this_round"] >= 2 or new_state["last_raiser"] == player:
            new_state = _advance_phase(new_state)
        else:
            new_state["current_player"] = opponent

    elif action == "K":
        # Check
        new_state["actions_this_round"] += 1

        # Both checked = end round
        if new_state["actions_this_round"] >= 2:
            new_state = _advance_phase(new_state)
        else:
            new_state["current_player"] = opponent

    elif action == "R":
        # Raise/Bet
        max_bet = max(new_state["bets"])
        call_amount = max_bet - new_state["bets"][player]
        raise_amount = min(BET_SIZE, new_state["stacks"][player] - call_amount)
        total = call_amount + raise_amount

        new_state["bets"][player] += total
        new_state["stacks"][player] -= total
        new_state["pot"] += total
        new_state["last_raiser"] = player
        new_state["actions_this_round"] += 1
        new_state["current_player"] = opponent

    return new_state


def get_current_player(state: State) -> int:
    """Returns current player: -1 for chance, 0/1 for players, -4 for terminal."""
    return state["current_player"]


def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    names = {0: "Small Blind", 1: "Big Blind", CHANCE_PLAYER: "Chance", TERMINAL_PLAYER: "Terminal"}
    return names.get(player_id, "Unknown")


def get_rewards(state: State) -> List[float]:
    """Returns rewards at terminal state."""
    if not state["terminal"]:
        return [0.0, 0.0]

    winner = state["winner"]
    pot = state["pot"]

    if winner == 0:
        # P0 wins - gets pot minus what they put in
        return [float(pot - state["bets"][0]), float(-state["bets"][1])]
    elif winner == 1:
        return [float(-state["bets"][0]), float(pot - state["bets"][1])]
    else:
        # Tie - split pot
        half = pot / 2
        return [float(half - state["bets"][0]), float(half - state["bets"][1])]


def get_observations(state: State) -> List[PlayerObservation]:
    """Returns observations for each player."""
    obs = []
    for p in range(NUM_PLAYERS):
        # Filter history to only show public actions (no hole card deals)
        # Board deals are public, betting actions are public
        public_history = [a for a in state["history"] if not a.startswith("deal:")]

        obs.append({
            "my_hole_cards": list(state["hole_cards"][p]),
            "board": list(state["board"]),
            "pot": state["pot"],
            "my_stack": state["stacks"][p],
            "opp_stack": state["stacks"][1 - p],
            "my_bet": state["bets"][p],
            "opp_bet": state["bets"][1 - p],
            "phase": state["phase"],
            "player_id": p,
            "terminal": state["terminal"],
            "history": public_history
        })
    return obs


def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]],
                     player_id: int,
                     last_is_terminal: bool = False) -> List[Action]:
    """
    Reconstruct a plausible action history consistent with player's observations.
    Opponent's hole cards are randomly sampled; board cards are known.
    """
    if not obs_action_history:
        return []

    # Get the most complete observation (last one with most info)
    final_obs = obs_action_history[-1][0]
    last_action = obs_action_history[-1][1]
    my_hole = list(final_obs.get("my_hole_cards", []))
    board = list(final_obs.get("board", []))

    # Cards we know
    known_cards = set(my_hole + board)

    # Create a deck without known cards
    full_deck = _create_deck()
    remaining = [c for c in full_deck if c not in known_cards]

    # Sample opponent's hole cards
    random.shuffle(remaining)
    opp_hole = remaining[:2] if len(remaining) >= 2 else remaining

    # Reconstruct full action history
    history = []

    # 1. Deal hole cards: P0 gets 2, then P1 gets 2
    p0_hole = my_hole if player_id == 0 else opp_hole
    p1_hole = opp_hole if player_id == 0 else my_hole

    for card in p0_hole:
        history.append(f"deal:{card}")
    for card in p1_hole:
        history.append(f"deal:{card}")

    # 2. Use the observation's betting history and insert board deals when needed
    # The obs["history"] contains all betting actions (both players)
    obs_betting_history = final_obs.get("history", [])

    # Track which board cards we've dealt
    board_idx = 0
    actions_since_last_deal = 0

    # We need to figure out where board deals occur based on the game flow
    # Preflop ends after both players act and bets are equal
    # Then flop (3 cards), then turn (1 card), then river (1 card)

    # Replay the game to determine when board cards were dealt
    replay_state = get_initial_state()

    # Apply hole card deals
    for card in p0_hole:
        replay_state = apply_action(replay_state, f"deal:{card}")
    for card in p1_hole:
        replay_state = apply_action(replay_state, f"deal:{card}")

    # Now add betting actions, inserting board deals when phase changes
    for action in obs_betting_history:
        # Check if we need to deal board cards before this action
        while replay_state["current_player"] == CHANCE_PLAYER and board_idx < len(board):
            history.append(f"deal:{board[board_idx]}")
            replay_state = apply_action(replay_state, f"deal:{board[board_idx]}")
            board_idx += 1

        # Add the betting action
        history.append(action)
        replay_state = apply_action(replay_state, action)

        # If game ended (fold), stop
        if replay_state["terminal"]:
            break

    # Always add the final action - observation is captured BEFORE the action,
    # so the player's action is never in obs_betting_history
    if last_action is not None:
        # Check if we need board deals first
        while replay_state["current_player"] == CHANCE_PLAYER and board_idx < len(board):
            history.append(f"deal:{board[board_idx]}")
            replay_state = apply_action(replay_state, f"deal:{board[board_idx]}")
            board_idx += 1

        history.append(last_action)

    return history
