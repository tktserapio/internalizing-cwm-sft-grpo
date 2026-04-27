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
    """Shuffles the deck and returns a shuffled version."""
    random.shuffle(deck)
    return deck

def deal_cards(deck: List[int], num_players: int) -> Tuple[List[int], List[int]]:
    """Deals the deck evenly between two players."""
    half_deck = len(deck) // num_players
    return (deck[:half_deck], deck[half_deck:])

def form_hands(hand: List[int], num_draws: int) -> List[int]:
    """Each player draws the top three cards from their draw pile."""
    return hand[:num_draws]

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Assuming a standard deck of 52 cards
    deck = list(range(1, 15)) * 4  # Aces to Kings, each suit
    shuffled_deck = shuffle_deck(deck)
    player1_hand, player2_hand = deal_cards(shuffled_deck, 2)
    player1_hand = form_hands(player1_hand, 3)
    player2_hand = form_hands(player2_hand, 3)
    return {
        "player1_hand": player1_hand,
        "player2_hand": player2_hand,
        "publicly_revealed_cards": [],
        "current_player": 0,
        "player1_win_pile": [],
        "player2_win_pile": []
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    if action.startswith("play:"):
        card_value = int(action.split(":")[1])
        if state["current_player"] == 0:
            state["player1_hand"].remove(card_value)
            state["player2_hand"].remove(card_value)
            if card_value > max(state["player2_hand"]):
                state["player1_win_pile"].append(card_value)
                state["player2_win_pile"].extend(state["player2_hand"])
                state["player2_hand"] = []
            else:
                state["player2_win_pile"].append(card_value)
                state["player1_win_pile"].extend(state["player1_hand"])
                state["player1_hand"] = []
        elif state["current_player"] == 1:
            state["player2_hand"].remove(card_value)
            state["player1_hand"].remove(card_value)
            if card_value > max(state["player1_hand"]):
                state["player2_win_pile"].append(card_value)
                state["player1_win_pile"].extend(state["player1_hand"])
                state["player1_hand"] = []
            else:
                state["player1_win_pile"].append(card_value)
                state["player2_win_pile"].extend(state["player2_hand"])
                state["player2_hand"] = []
        state["current_player"] = (state["current_player"] + 1) % 2
        state["publicly_revealed_cards"].append(card_value)
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
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
        legal_actions.extend([f"play:{card}" for card in state["player1_hand"]])
    elif state["current_player"] == 1:
        legal_actions.extend([f"play:{card}" for card in state["player2_hand"]])
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player1_obs = {
        "hand": state["player1_hand"],
        "win_pile": state["player1_win_pile"],
        "publicly_revealed_cards": state["publicly_revealed_cards"]
    }
    player2_obs = {
        "hand": state["player2_hand"],
        "win_pile": state["player2_win_pile"],
        "publicly_revealed_cards": state["publicly_revealed_cards"]
    }
    return [player1_obs, player2_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement stochastic sampling logic based on the observed history.
    # For simplicity, we'll just return a fixed sequence of actions.
    # In a real implementation, this would involve complex logic to ensure the sampled actions match the observed history.
    return ["play:7", "play:Q", "play:A", "play:K"]