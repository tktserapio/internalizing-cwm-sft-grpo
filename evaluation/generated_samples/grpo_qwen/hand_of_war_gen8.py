import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper functions
def shuffle_deck(deck: List[int]) -> List[int]:
    """Shuffles the deck."""
    random.shuffle(deck)
    return deck

def deal_cards(deck: List[int], num_players: int) -> Tuple[List[int], List[int]]:
    """Deals cards evenly between players."""
    half_deck = len(deck) // num_players
    return (deck[:half_deck], deck[half_deck:])

def form_hands(hand: List[int]) -> List[int]:
    """Each player draws the top three cards from their draw pile."""
    return hand[:3]

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Deck of cards (Ace through King)
    deck = list(range(1, 15))
    # Shuffle the deck
    shuffled_deck = shuffle_deck(deck)
    # Deal the deck evenly between two players
    player1_hand, player2_hand = deal_cards(shuffled_deck, 2)
    # Form hands
    player1_hand = form_hands(player1_hand)
    player2_hand = form_hands(player2_hand)
    # Initial state
    return {
        "player1_hand": player1_hand,
        "player2_hand": player2_hand,
        "publicly_revealed_cards": [],
        "current_player": 0,
        "player1_win_pile": [],
        "player2_win_pile": [],
        "draw_piles": {"player1": player1_hand, "player2": player2_hand},
        "showdowns": []
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    if action.startswith("play:"):
        card_index = int(action.split(":")[1])
        if card_index < len(new_state["player1_hand"]):
            new_state["player1_hand"][card_index] = 0  # Mark as played
            new_state["publicly_revealed_cards"].append(card_index)
            new_state["current_player"] = 1
            return new_state
        elif card_index < len(new_state["player1_hand"]) + len(new_state["player2_hand"]):
            new_state["player2_hand"][card_index - len(new_state["player1_hand"])] = 0  # Mark as played
            new_state["publicly_revealed_cards"].append(card_index - len(new_state["player1_hand"]))
            new_state["current_player"] = 0
            return new_state
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    player1_win_pile = len(state["player1_win_pile"])
    player2_win_pile = len(state["player2_win_pile"])
    if player1_win_pile == 16:
        return [1.0, 0.0]
    elif player2_win_pile == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    if state["current_player"] == 0:
        legal_actions.append(f"play:{state['player1_hand'][0]}")
        if len(state["player1_hand"]) > 1:
            legal_actions.append(f"play:{state['player1_hand'][1]}")
        if len(state["player1_hand"]) > 2:
            legal_actions.append(f"play:{state['player1_hand'][2]}")
    else:
        legal_actions.append(f"play:{state['player2_hand'][0]}")
        if len(state["player2_hand"]) > 1:
            legal_actions.append(f"play:{state['player2_hand'][1]}")
        if len(state["player2_hand"]) > 2:
            legal_actions.append(f"play:{state['player2_hand'][2]}")
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player1_obs = {
        "hand": state["player1_hand"],
        "win_pile": state["player1_win_pile"],
        "draw_pile": state["draw_piles"]["player1"]
    }
    player2_obs = {
        "hand": state["player2_hand"],
        "win_pile": state["player2_win_pile"],
        "draw_pile": state["draw_piles"]["player2"]
    }
    return [player1_obs, player2_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    # This should be replaced with actual resampling logic
    return [
        f"play:{obs_action_history[-1][0]['hand'][0]}" if obs_action_history[-1][1] is None else obs_action_history[-1][1],
        f"play:{obs_action_history[-1][0]['hand'][1]}" if obs_action_history[-1][1] is None else obs_action_history[-1][1],
        f"play:{obs_action_history[-1][0]['hand'][2]}" if obs_action_history[-1][1] is None else obs_action_history[-1][1]
    ]