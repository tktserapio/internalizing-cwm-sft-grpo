import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initialize the deck and shuffle it
    deck = list(range(1, 53))
    random.shuffle(deck)
    # Deal the cards
    dealer_hand = deck[:26]
    upcard = deck[26]
    stockpile = deck[27:]
    
    # Initial state
    state = {
        "dealer_hand": dealer_hand,
        "upcard": upcard,
        "stockpile": stockpile,
        "knocked": False,
        "knock_card": None,
        "round": 1,
        "player_0_deadwood": 0,
        "player_1_deadwood": 0,
        "player_0_melds": [],
        "player_1_melds": [],
        "player_0_meld_value": 0,
        "player_1_meld_value": 0,
        "player_0_deadwood_value": 0,
        "player_1_deadwood_value": 0,
        "phase": "Draw",
        "player": 0
    }
    return state

# Apply action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == "Draw stock":
        new_state["stockpile"].append(new_state["upcard"])
        new_state["upcard"] = new_state["stockpile"].pop()
        new_state["phase"] = "Discard"
    elif action == "Draw upcard":
        new_state["stockpile"].append(new_state["upcard"])
        new_state["upcard"] = new_state["stockpile"].pop()
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        new_state["dealer_hand"].remove(card_to_discard)
        new_state["stockpile"].append(card_to_discard)
        new_state["phase"] = "Knock"
    elif action == "Knock":
        new_state["knocked"] = True
        new_state["knock_card"] = new_state["upcard"]
        new_state["phase"] = "Layoff"
    elif action == "Done":
        new_state["knocked"] = True
        new_state["phase"] = "Layoff"
    elif action == "Pass":
        new_state["phase"] = "Draw"
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

# Get current player
def get_current_player(state: State) -> int:
    return state["player"]

# Get player name
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards
def get_rewards(state: State) -> List[float]:
    if state["knocked"]:
        return [state["player_1_deadwood_value"] - state["player_0_deadwood_value"], state["player_0_deadwood_value"] - state["player_1_deadwood_value"]]
    return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> List[Action]:
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Knock":
        return ["Knock", "Done"]
    elif state["phase"] == "Layoff":
        return ["Action: " + card for card in state["dealer_hand"]]
    return []

# Get observations
def get_observations(state: State) -> List[PlayerObservation]:
    player_0_obs = {
        "dealer_hand": state["dealer_hand"],
        "upcard": state["upcard"],
        "knock_card": state["knock_card"],
        "player_0_deadwood": state["player_0_deadwood"],
        "player_1_deadwood": state["player_1_deadwood"],
        "player_0_melds": state["player_0_melds"],
        "player_1_melds": state["player_1_melds"],
        "player_0_meld_value": state["player_0_meld_value"],
        "player_1_meld_value": state["player_1_meld_value"],
        "player_0_deadwood_value": state["player_0_deadwood_value"],
        "player_1_deadwood_value": state["player_1_deadwood_value"],
        "phase": state["phase"],
        "player": state["player"]
    }
    player_1_obs = {
        "dealer_hand": state["dealer_hand"],
        "upcard": state["upcard"],
        "knock_card": state["knock_card"],
        "player_0_deadwood": state["player_1_deadwood"],
        "player_1_deadwood": state["player_0_deadwood"],
        "player_0_melds": state["player_1_melds"],
        "player_1_melds": state["player_0_melds"],
        "player_0_meld_value": state["player_1_meld_value"],
        "player_1_meld_value": state["player_0_meld_value"],
        "player_0_deadwood_value": state["player_1_deadwood_value"],
        "player_1_deadwood_value": state["player_0_deadwood_value"],
        "phase": state["phase"],
        "player": state["player"]
    }
    return [player_0_obs, player_1_obs]

# Resample history
def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would need to implement the logic to randomly sample valid sequences of actions
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ["Draw stock", "Action: 2s", "Knock"]
    else:
        return ["Draw stock", "Action: 2s", "Knock"]