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

# Helper function to initialize the state
def get_initial_state():
    # Initialize the deck and shuffle it
    deck = list(range(1, 53))
    random.shuffle(deck)
    # Deal the cards
    dealer_hand = deck[:26]
    upcard = deck[26]
    stockpile = deck[27:]
    # Create the initial state
    return {
        "dealer_hand": dealer_hand,
        "upcard": upcard,
        "stockpile": stockpile,
        "phase": "Draw",
        "knock_card": None,
        "knocked_by": None,
        "knocked_on": None,
        "deadwood": {"player_0": 0, "player_1": 0},
        "melds": {"player_0": [], "player_1": []}
    }

# Apply action function
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == "Draw stock":
        new_state["stockpile"].append(new_state["upcard"])
        new_state["upcard"] = new_state["stockpile"].pop()
        new_state["phase"] = "Discard"
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["stockpile"].pop()
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        new_state["dealer_hand"].remove(card_to_discard)
        new_state["stockpile"].append(card_to_discard)
        new_state["phase"] = "Knock"
    elif action == "Knock":
        new_state["knock_card"] = new_state["upcard"]
        new_state["knocked_by"] = get_current_player(new_state)
        new_state["phase"] = "Layoff"
    elif action == "Done":
        new_state["phase"] = "Layoff"
    elif action == "Pass":
        new_state["phase"] = "Layoff"
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

# Get current player function
def get_current_player(state: State) -> int:
    return 0 if state["knocked_by"] == 1 else 1

# Get player name function
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards function
def get_rewards(state: State) -> list[float]:
    if state["phase"] == "Wall":
        return [0.0, 0.0]
    elif state["phase"] == "Layoff":
        knocker_deadwood = state["deadwood"][f"player_{state['knocked_by']}"]
        opponent_deadwood = state["deadwood"][f"player_{1 - state['knocked_by']}"]
        if knocker_deadwood <= opponent_deadwood:
            return [opponent_deadwood - knocker_deadwood + 25, knocker_deadwood]
        elif knocker_deadwood == 0:
            return [0.0, 0.0 + 25]
        else:
            return [0.0, knocker_deadwood]
    else:
        return [0.0, 0.0]

# Get legal actions function
def get_legal_actions(state: State) -> list[Action]:
    if state["phase"] == "Wall":
        return []
    elif state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Knock":
        return ["Knock", "Done"]
    elif state["phase"] == "Layoff":
        return ["Pass"]
    else:
        raise ValueError("Invalid phase")

# Get observations function
def get_observations(state: State) -> list[PlayerObservation]:
    dealer_hand = state["dealer_hand"]
    upcard = state["upcard"]
    stockpile = state["stockpile"]
    deadwood = state["deadwood"]
    melds = state["melds"]
    observations = [
        {
            "dealer_hand": dealer_hand,
            "upcard": upcard,
            "stockpile": stockpile,
            "deadwood": deadwood[f"player_0"],
            "melds": melds[f"player_0"]
        },
        {
            "dealer_hand": dealer_hand,
            "upcard": upcard,
            "stockpile": stockpile,
            "deadwood": deadwood[f"player_1"],
            "melds": melds[f"player_1"]
        }
    ]
    return observations

# Resample history function
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # This function would need to be implemented based on the specific rules and logic of the game.
    # For simplicity, we'll just return a fixed sequence of actions.
    # In a real implementation, this function should generate a stochastic sequence of actions.
    # Here, we're returning a fixed sequence of actions for demonstration purposes.
    if obs_action_history[-1][1] == "Knock":
        return ["Action: 3d", "Knock", "Done"]
    else:
        return ["Draw stock", "Draw upcard", "Action: 3d", "Knock", "Done"]

# Example usage
initial_state = get_initial_state()
print(initial_state)