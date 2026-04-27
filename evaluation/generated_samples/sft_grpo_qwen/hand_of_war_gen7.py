import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import List, Dict, Any, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def parse_deck(deck: List[int]) -> List[int]:
    """Parses the deck into a shuffled list of integers representing card ranks."""
    return sorted(deck, key=lambda x: x % 13, reverse=True)

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = list(range(1, 53))  # Deck of cards from Aces to Kings
    shuffled_deck = parse_deck(deck)
    player0_hand = shuffled_deck[:9]
    player1_hand = shuffled_deck[9:18]
    public_revealed_cards = []
    return {
        "deck": shuffled_deck,
        "player0_hand": player0_hand,
        "player1_hand": player1_hand,
        "public_revealed_cards": public_revealed_cards,
        "player0_win_pile": [],
        "player1_win_pile": [],
        "current_player": 0,
        "draw_pile": shuffled_deck[18:],
        "showdown_count": 0,
        "showdown_winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if action.startswith("play:"):
        card_index = int(action.split(":")[1])
        new_state["public_revealed_cards"].append(state[f"player{new_state['current_player']}_hand"][card_index])
        new_state[f"player{new_state['current_player']}_hand"].pop(card_index)
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
        return new_state
    elif action.startswith("deal:"):
        cards_to_deal = action.split(",")[:3]
        new_state["draw_pile"] += [int(card) for card in cards_to_deal]
        return new_state
    else:
        raise ValueError(f"Invalid action: {action}")

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    player0_win_pile = len(state["player0_win_pile"])
    player1_win_pile = len(state["player1_win_pile"])
    if player0_win_pile == 16:
        return [1.0, 0.0]
    elif player1_win_pile == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = get_current_player(state)
    if current_player == -4:
        return []
    elif current_player == 0:
        return ["play:" + str(i) for i in range(3)]
    else:
        return ["deal:" + ",".join(map(str, state["draw_pile"][:3]))]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player0_obs = {
        "hand": state["player0_hand"],
        "win_pile": state["player0_win_pile"],
        "draw_pile": state["draw_pile"]
    }
    player1_obs = {
        "hand": state["player1_hand"],
        "win_pile": state["player1_win_pile"],
        "draw_pile": state["draw_pile"]
    }
    return [player0_obs, player1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we assume a deterministic resampling here
    if player_id == 0:
        return ["play:0", "deal:1,2,3"]
    else:
        return ["deal:4,5,6", "play:1"]