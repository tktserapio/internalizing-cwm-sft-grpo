import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initial state setup
    state = {
        "deck": list(range(1, 53)),  # Full deck excluding jokers
        "upcard": None,              # Upcard is not yet revealed
        "dealer": 0,                 # Dealer starts as player 0
        "knock_card": 10,            # Default knock card value
        "round": 1,                  # Round counter
        "phase": "Draw",             # Initial phase
        "player_0_hand": [],
        "player_1_hand": [],
        "player_0_deadwood": 0,
        "player_1_deadwood": 0,
        "player_0_melds": [],
        "player_1_melds": []
    }
    return state

# Apply an action to the current state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == "Draw stock":
        new_state["deck"].append(new_state["deck"].pop(0))
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["deck"].pop(0)
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        new_state["player_0_hand"].remove(card_to_discard)
        new_state["player_1_hand"].remove(card_to_discard)
        new_state["player_0_deadwood"] += card_to_discard_to_value(card_to_discard)
        new_state["player_1_deadwood"] += card_to_discard_to_value(card_to_discard)
    elif action == "Action: Knock":
        new_state["phase"] = "Knock"
    elif action == "Action: Done":
        new_state["phase"] = "Knock"
    elif action == "Pass":
        new_state["phase"] = "Discard"
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state["dealer"]

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards per player
def get_rewards(state: State) -> List[float]:
    player_0_deadwood = state["player_0_deadwood"]
    player_1_deadwood = state["player_1_deadwood"]
    if state["phase"] == "Wall":
        return [0.0, 0.0]
    elif state["phase"] == "Knock":
        if player_0_deadwood <= player_1_deadwood:
            return [player_1_deadwood - player_0_deadwood, 0.0]
        else:
            return [0.0, player_0_deadwood - player_1_deadwood + 25.0]
    else:
        return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    current_player = get_current_player(state)
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Knock":
        if current_player == 0:
            return ["Action: Knock", "Action: Done"]
        else:
            return ["Action: Knock"]
    elif state["phase"] == "Discard":
        return ["Action: " + card for card in state["player_0_hand"]]
    else:
        return []

# Get observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    player_0_obs = {
        "phase": state["phase"],
        "dealer": state["dealer"],
        "upcard": state["upcard"],
        "player_0_hand": state["player_0_hand"],
        "player_0_deadwood": state["player_0_deadwood"],
        "player_1_hand": state["player_1_hand"],
        "player_1_deadwood": state["player_1_deadwood"],
        "player_0_melds": state["player_0_melds"],
        "player_1_melds": state["player_1_melds"]
    }
    player_1_obs = {
        "phase": state["phase"],
        "dealer": state["dealer"],
        "upcard": state["upcard"],
        "player_0_hand": state["player_1_hand"],
        "player_0_deadwood": state["player_1_deadwood"],
        "player_1_hand": state["player_0_hand"],
        "player_0_melds": state["player_1_melds"],
        "player_1_melds": state["player_0_melds"]
    }
    return [player_0_obs, player_1_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ["Draw stock", "Action: 2c", "Action: 3c", "Action: 4c", "Action: Knock"]
    else:
        return ["Draw stock", "Action: 2d", "Action: 3d", "Action: 4d", "Action: Knock"]

# Helper function to convert card to its value
def card_to_value(card: str) -> int:
    return int(card[1])

# Helper function to convert card to its value in points
def card_to_discard_value(card: str) -> int:
    value = card_to_value(card)
    if value > 10:
        return 10
    elif value == 1:
        return 1
    else:
        return value

# Convert card to its value in points
def card_to_discard_value(card: str) -> int:
    return card_to_discard_value(card)

# Convert card to its value in points
def card_to_value(card: str) -> int:
    return int(card[1])