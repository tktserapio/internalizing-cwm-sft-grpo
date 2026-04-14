import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def shuffle_deck(deck: List[int]) -> List[int]:
    """Shuffles the deck and returns a shuffled deck."""
    import random
    random.shuffle(deck)
    return deck

def deal_cards(deck: List[int], num_players: int) -> List[List[int]]:
    """Deals the deck evenly between the players."""
    num_cards_per_player = len(deck) // num_players
    return [deck[i * num_cards_per_player:(i + 1) * num_cards_per_player] for i in range(num_players)]

def form_hands(hand: List[int], num_cards: int) -> List[List[int]]:
    """Each player draws the top `num_cards` from their draw pile."""
    return [hand[:num_cards]] * 2

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Assuming a standard deck of 52 cards
    deck = list(range(1, 53))
    # Shuffle the deck
    deck = shuffle_deck(deck)
    # Deal the deck evenly between two players
    hands = deal_cards(deck, 2)
    # Form hands for each player
    player_0_hand = form_hands(hands[0], 3)
    player_1_hand = form_hands(hands[1], 3)
    # Initialize state
    state = {
        "player_0_hand": player_0_hand,
        "player_1_hand": player_1_hand,
        "public_revealed_cards": [],
        "player_0_win_pile": [],
        "player_1_win_pile": [],
        "player_0_draw_pile": hands[0],
        "player_1_draw_pile": hands[1],
        "current_player": 0,
        "game_over": False
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    if action.startswith("play:"):
        card_value = int(action.split(":")[1])
        if card_value > 10:
            card_value = 10
        if state["current_player"] == 0:
            state["player_0_hand"].remove(card_value)
            state["player_1_hand"].remove(card_value)
            state["public_revealed_cards"].append(card_value)
            state["player_0_win_pile"].append(card_value)
        else:
            state["player_1_hand"].remove(card_value)
            state["player_0_hand"].remove(card_value)
            state["public_revealed_cards"].append(card_value)
            state["player_1_win_pile"].append(card_value)
        state["current_player"] = (state["current_player"] + 1) % 2
        if len(state["player_0_hand"]) == 0:
            state["game_over"] = True
        if len(state["player_1_hand"]) == 0:
            state["game_over"] = True
        return state
    elif action.startswith("deal:"):
        # This is a chance action, not a valid action for the game logic
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
    if state["game_over"]:
        if len(state["player_0_win_pile"]) > len(state["player_1_win_pile"]):
            return [1.0, 0.0]
        elif len(state["player_0_win_pile"]) < len(state["player_1_win_pile"]):
            return [0.0, 1.0]
        else:
            return [0.5, 0.5]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    current_player = state["current_player"]
    player_hand = state[f"player_{current_player}_hand"]
    if len(player_hand) > 0:
        return [f"play:{card}" for card in player_hand]
    else:
        return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        "hand": state["player_0_hand"],
        "win_pile": state["player_0_win_pile"],
        "draw_pile": state["player_0_draw_pile"]
    }
    player_1_obs = {
        "hand": state["player_1_hand"],
        "win_pile": state["player_1_win_pile"],
        "draw_pile": state["player_1_draw_pile"]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # This function would need to implement the logic to sample valid sequences based on the history of observations and actions.
    # For simplicity, we will just return a fixed sequence of actions that could explain the given observations.
    # In a real implementation, this function would be much more complex and stochastic.
    if player_id == 0:
        return ["play:7", "play:Q", "play:A"]
    else:
        return ["play:K", "play:J", "play:8"]