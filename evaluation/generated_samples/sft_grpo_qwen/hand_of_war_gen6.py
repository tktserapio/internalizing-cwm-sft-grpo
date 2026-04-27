import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import List, Dict, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def parse_deck(deck: List[str]) -> Dict[int, List[str]]:
    """Parses the deck into a dictionary of player hands."""
    player0_hand = deck[:8]
    player1_hand = deck[8:]
    return {"player0_hand": player0_hand, "player1_hand": player1_hand}

def shuffle_deck(deck: List[str]) -> List[str]:
    """Shuffles the deck and returns a shuffled version."""
    import random
    random.shuffle(deck)
    return deck

def deal_cards(deck: List[str], num_players: int) -> Dict[int, List[str]]:
    """Deals cards evenly between players."""
    num_cards_per_player = len(deck) // num_players
    return {i: deck[i * num_cards_per_player:(i + 1) * num_cards_per_player] for i in range(num_players)}

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = ["A", "K", "Q", "J"] * 4  # Assuming a standard deck of 16 cards
    shuffled_deck = shuffle_deck(deck)
    player0_hand = shuffled_deck[:8]
    player1_hand = shuffled_deck[8:]
    return {
        "deck": shuffled_deck,
        "player0_hand": player0_hand,
        "player1_hand": player1_hand,
        "publicly_revealed_cards": [],
        "current_player": 0,
        "player0_win_pile": [],
        "player1_win_pile": [],
        "player0_draw_pile": player0_hand,
        "player1_draw_pile": player1_hand,
        "player0_score": 0,
        "player1_score": 0
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    if action.startswith("play:"):
        card_value = action.split(":")[1]
        current_player = state["current_player"]
        if current_player == 0:
            state["player0_draw_pile"].remove(card_value)
            state["player0_win_pile"].append(card_value)
            state["player0_score"] += 1
        else:
            state["player1_draw_pile"].remove(card_value)
            state["player1_win_pile"].append(card_value)
            state["player1_score"] += 1
        state["current_player"] = (state["current_player"] + 1) % 2
        state["publicly_revealed_cards"].append(card_value)
        return state
    elif action.startswith("deal:"):
        cards_to_deal = action.split(",")[:8]
        state["player0_draw_pile"] = state["player0_draw_pile"][8:] + cards_to_deal
        state["player1_draw_pile"] = state["player1_draw_pile"][8:] + cards_to_deal
        return state
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
    return [state["player0_score"], state["player1_score"]]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = state["current_player"]
    if state["player0_draw_pile"] and state["player1_draw_pile"]:
        return ["play:" + card for card in state["player0_draw_pile"] + state["player1_draw_pile"]]
    else:
        return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player0_obs = {
        "deck": state["deck"],
        "draw_pile": state["player0_draw_pile"],
        "win_pile": state["player0_win_pile"],
        "score": state["player0_score"]
    }
    player1_obs = {
        "deck": state["deck"],
        "draw_pile": state["player1_draw_pile"],
        "win_pile": state["player1_win_pile"],
        "score": state["player1_score"]
    }
    return [player0_obs, player1_obs]

def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    return [
        "play:A",
        "play:K",
        "play:Q",
        "play:J",
        "play:A",
        "play:K",
        "play:Q",
        "play:J"
    ]