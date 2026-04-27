import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Dict, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def shuffle_deck() -> List[int]:
    """Shuffles a standard 52-card deck and returns the shuffled order."""
    deck = list(range(1, 53))
    random.shuffle(deck)
    return deck

def create_initial_state(deck: List[int]) -> State:
    """Creates the initial game state."""
    # Initial state setup
    state = {
        "deck": deck,
        "upcard": deck.pop(0),
        "dealer": 0,  # Assume player 0 is the dealer
        "phase": "Draw",
        "knock_card": 10,  # Default knock card value
        "player_0_melds": [],
        "player_1_melds": [],
        "player_0_deadwood": 0,
        "player_1_deadwood": 0,
        "player_0_hand": deck[:13],
        "player_1_hand": deck[13:26],
        "player_0_turn": True,
        "player_1_turn": False,
        "player_0_score": 0,
        "player_1_score": 0
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Applies an action to the current state and returns the new state."""
    new_state = state.copy()
    if action == "Draw stock":
        new_state["deck"].append(new_state["upcard"])
        new_state["upcard"] = new_state["deck"].pop(0)
    elif action == "Draw upcard":
        new_state["deck"].append(new_state["upcard"])
        new_state["upcard"] = new_state["deck"].pop(0)
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        new_state["deck"].append(card_to_discard)
        new_state["upcard"] = card_to_discard
        new_state["player_0_hand"].remove(card_to_discard)
        new_state["player_1_hand"].remove(card_to_discard)
        new_state["player_0_turn"], new_state["player_1_turn"] = new_state["player_1_turn"], new_state["player_0_turn"]
    elif action == "Action: Knock":
        new_state["knock_phase"] = True
        new_state["knock_card"] = new_state["player_0_deadwood"] + new_state["player_1_deadwood"]
        new_state["player_0_melds"], new_state["player_1_melds"] = [], []
        new_state["player_0_deadwood"], new_state["player_1_deadwood"] = 0, 0
    elif action == "Action: Done":
        new_state["knock_phase"] = False
    elif action == "Pass":
        new_state["player_0_turn"], new_state["player_1_turn"] = new_state["player_1_turn"], new_state["player_0_turn"]
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    """Returns the current player (0 or 1)."""
    return state["player_0_turn"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["knock_phase"]:
        return [state["player_0_deadwood"], state["player_1_deadwood"]]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for the current state."""
    if state["knock_phase"]:
        return ["Action: Done"]
    elif state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    else:
        return ["Action: Knock", "Action: Done"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns the observations for each player."""
    player_0_obs = {
        "phase": state["phase"],
        "upcard": state["upcard"],
        "dealer": state["dealer"],
        "deck": state["deck"],
        "knock_card": state["knock_card"],
        "player_0_melds": state["player_0_melds"],
        "player_1_melds": state["player_1_melds"],
        "player_0_deadwood": state["player_0_deadwood"],
        "player_1_deadwood": state["player_1_deadwood"],
        "player_0_hand": state["player_0_hand"],
        "player_1_hand": state["player_1_hand"],
        "player_0_turn": state["player_0_turn"],
        "player_1_turn": state["player_1_turn"]
    }
    player_1_obs = {
        "phase": state["phase"],
        "upcard": state["upcard"],
        "dealer": state["dealer"],
        "deck": state["deck"],
        "knock_card": state["knock_card"],
        "player_0_melds": state["player_1_melds"],
        "player_1_melds": state["player_0_melds"],
        "player_0_deadwood": state["player_1_deadwood"],
        "player_1_deadwood": state["player_0_deadwood"],
        "player_0_hand": state["player_1_hand"],
        "player_1_hand": state["player_0_hand"],
        "player_0_turn": state["player_1_turn"],
        "player_1_turn": state["player_0_turn"]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions."""
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    # This should be replaced with actual resampling logic
    if player_id == 0:
        return ["Draw stock", "Action: 2s", "Action: 3s", "Action: 4s", "Action: Knock"]
    else:
        return ["Draw stock", "Action: 2s", "Action: 3s", "Action: 4s", "Action: Knock"]

# Main functions
def get_initial_state() -> State:
    """Returns the initial game state."""
    deck = shuffle_deck()
    return create_initial_state(deck)

def apply_action(state: State, action: Action) -> State:
    """Applies an action to the current state and returns the new state."""
    return apply_action(state, action)

def get_current_player(state: State) -> int:
    """Returns the current player (0 or 1)."""
    return get_current_player(state)

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return get_player_name(player_id)

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    return get_rewards(state)

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for the current state."""
    return get_legal_actions(state)

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns the observations for each player."""
    return get_observations(state)

def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions."""
    return resample_history(obs_action_history, player_id)