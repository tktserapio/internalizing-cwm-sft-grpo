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
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
DECK = [rank + suit for suit in SUITS for rank in RANKS]
KNOCK_CARD_VALUE = 10
GIN_BONUS = 25
UNDERCUT_BONUS = 25

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = DECK[:]
    random.shuffle(deck)
    player_hands = [deck[:10], deck[10:20]]
    stock_pile = deck[20:]
    discard_pile = [stock_pile.pop(0)]
    return {
        "player_hands": player_hands,
        "stock_pile": stock_pile,
        "discard_pile": discard_pile,
        "current_player": 0,
        "phase": "Draw",
        "scores": [0, 0],
        "round_over": False
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    player = new_state["current_player"]
    hand = new_state["player_hands"][player]

    if action == "Draw stock":
        hand.append(new_state["stock_pile"].pop(0))
        new_state["phase"] = "Discard"
    elif action == "Draw upcard":
        hand.append(new_state["discard_pile"].pop())
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card = action.split(": ")[1]
        hand.remove(card)
        new_state["discard_pile"].append(card)
        new_state["current_player"] = 1 - player
        new_state["phase"] = "Draw"
    elif action == "Action: Knock":
        new_state["round_over"] = True
        # Handle scoring and layoff logic here
    elif action == "Pass":
        new_state["current_player"] = 1 - player
        if new_state["phase"] == "Draw":
            new_state["phase"] = "Discard"

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state["round_over"] else state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state["round_over"]:
        return [0.0, 0.0]
    # Calculate rewards based on scoring logic
    return state["scores"]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["round_over"]:
        return []

    player = state["current_player"]
    hand = state["player_hands"][player]
    legal_actions = []

    if state["phase"] == "Draw":
        legal_actions.extend(["Draw stock", "Draw upcard"])
    elif state["phase"] == "Discard":
        legal_actions.extend([f"Action: {card}" for card in hand])
        if calculate_deadwood(hand) <= KNOCK_CARD_VALUE:
            legal_actions.append("Action: Knock")

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {"hand": state["player_hands"][0], "discard_pile": state["discard_pile"]},
        {"hand": state["player_hands"][1], "discard_pile": state["discard_pile"]}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Union[Action, None]]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions."""
    # This function would require more detailed logic to reconstruct a valid action sequence
    return []

def calculate_deadwood(hand: List[str]) -> int:
    """Calculate the deadwood value of a hand."""
    deadwood_value = 0
    # Implement logic to calculate deadwood value based on melds
    return deadwood_value

# Helper functions for scoring, meld detection, etc., would be added here.