import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple, Union

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
SUITS = ['S', 'C', 'D', 'H']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
KNOCK_CARD_VALUE = 10
GIN_BONUS = 25
UNDERCUT_BONUS = 25

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = [rank + suit for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    player_hands = [deck[:10], deck[10:20]]
    stock_pile = deck[20:]
    discard_pile = []
    return {
        "deck": deck,
        "player_hands": player_hands,
        "stock_pile": stock_pile,
        "discard_pile": discard_pile,
        "current_player": 0,
        "phase": "Draw",
        "round_over": False,
        "scores": [0, 0]
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    current_player = new_state["current_player"]
    player_hand = new_state["player_hands"][current_player]

    if action == "Draw stock":
        card = new_state["stock_pile"].pop(0)
        player_hand.append(card)
        new_state["phase"] = "Discard"
    elif action == "Draw upcard":
        card = new_state["discard_pile"].pop()
        player_hand.append(card)
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card = action.split(": ")[1]
        player_hand.remove(card)
        new_state["discard_pile"].append(card)
        new_state["current_player"] = 1 - current_player
        new_state["phase"] = "Draw"
    elif action == "Action: Knock":
        new_state["round_over"] = True
        new_state["phase"] = "Knock"
    elif action == "Pass":
        new_state["current_player"] = 1 - current_player

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["round_over"]:
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state["round_over"]:
        return [0.0, 0.0]

    # Calculate rewards based on deadwood and bonuses
    # Placeholder logic for scoring
    return [0.0, 0.0]  # Update with actual scoring logic

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["round_over"]:
        return []

    if state["phase"] == "Draw":
        actions = ["Draw stock"]
        if state["discard_pile"]:
            actions.append("Draw upcard")
        return actions
    elif state["phase"] == "Discard":
        player_hand = state["player_hands"][state["current_player"]]
        return [f"Action: {card}" for card in player_hand] + ["Action: Knock"]

    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {
            "hand": state["player_hands"][0],
            "discard_pile": state["discard_pile"],
            "phase": state["phase"]
        },
        {
            "hand": state["player_hands"][1],
            "discard_pile": state["discard_pile"],
            "phase": state["phase"]
        }
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Union[Action, None]]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # Placeholder for resampling logic
    return []

# Helper functions can be added here to handle specific game logic, such as scoring, melding, etc.