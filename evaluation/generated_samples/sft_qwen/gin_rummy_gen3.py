import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import *

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to shuffle a deck
def shuffle_deck() -> list[int]:
    deck = list(range(1, 53))
    random.shuffle(deck)
    return deck

# Initial state of the game
def get_initial_state() -> State:
    # Initialize the deck
    deck = shuffle_deck()
    # Deal the first upcard to the non-dealer
    upcard = deck.pop(0)
    # Create the initial state
    state = {
        "deck": deck,
        "upcard": upcard,
        "dealer": 0,  # Assume player 0 is the dealer
        "current_player": 0,
        "knock_card": 10,  # Default knock card value
        "knocked": False,
        "deadwood": {0: [], 1: []},
        "melds": {0: [], 1: []}
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == "Draw stock":
        new_state["deck"].append(new_state["upcard"])
        new_state["upcard"] = new_state["deck"].pop(0)
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        new_state["deck"].append(card_to_discard)
        new_state["upcard"] = new_state["deck"].pop(0)
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
        new_state["deadwood"][new_state["current_player"]].append(int(card_to_discard))
    elif action == "Knock":
        new_state["knocked"] = True
        new_state["knock_card"] = 10  # Default knock card value
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
    elif action == "Done":
        new_state["knocked"] = True
        new_state["knock_card"] = 10  # Default knock card value
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
    elif action == "Pass":
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state["current_player"]

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards per player
def get_rewards(state: State) -> list[float]:
    if state["knocked"]:
        return [0.0, 0.0]  # No rewards yet, waiting for layoff
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    current_player = get_current_player(state)
    if state["knocked"]:
        return ["Knock", "Done"]
    if state["knock_card"] > 10:
        return ["Draw stock", "Draw upcard"]
    return ["Draw stock", "Draw upcard", "Action: 2c", "Action: 3d", "Pass"]

# Get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    current_player = get_current_player(state)
    deadwood = state["deadwood"][current_player]
    melds = state["melds"][current_player]
    upcard = state["upcard"]
    observations = [
        {
            "deadwood": deadwood,
            "melds": melds,
            "upcard": upcard
        },
        {
            "deadwood": state["deadwood"][1 - current_player],
            "melds": state["melds"][1 - current_player],
            "upcard": state["upcard"]
        }
    ]
    return observations

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # For simplicity, we assume that the history is a complete trajectory
    # and we just need to return the last action taken by the current player
    last_action = obs_action_history[-1][1]
    if last_action is None:
        # If the last action was a pass, we need to generate a valid action
        if player_id == 0:
            return ["Draw stock"]
        else:
            return ["Draw stock", "Action: 2c"]
    return [last_action]

# Example usage
if __name__ == "__main__":
    state = get_initial_state()
    print("Initial state:", state)
    print("Legal actions:", get_legal_actions(state))