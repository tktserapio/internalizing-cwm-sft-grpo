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

# Helper function to initialize the game state
def get_initial_state():
    # Initialize the deck
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
        "knock_card_value": 10,
        "player_0_deadwood": 0,
        "player_1_deadwood": 0,
        "phase": "Draw",
        "player_0_melds": [],
        "player_1_melds": []
    }
    return state

# Apply an action to the game state
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
        if new_state["phase"] == "Knock":
            new_state["knocked"] = True
        new_state["phase"] = "Knock"
    elif action == "Action: Knock":
        new_state["knocked"] = True
        new_state["phase"] = "Layoff"
        new_state["knock_card_value"] = 10
        # Logic to declare melds and lay off cards
        # For simplicity, we'll just simulate declaring melds here
        new_state["player_0_melds"] = ["7c8c9cTc"]
        new_state["player_1_melds"] = ["9dTdJdQd"]
    elif action == "Action: Done":
        new_state["phase"] = "Layoff"
    elif action == "Pass":
        new_state["phase"] = "Layoff"
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return 0 if state["phase"] != "Knock" else 1

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    if state["phase"] == "Wall":
        return [0.0, 0.0]
    elif state["knocked"]:
        return [0.0, 0.0]
    else:
        return [state["player_0_deadwood"], state["player_1_deadwood"]]

# Get legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Knock":
        if state["knocked"]:
            return ["Action: Done"]
        else:
            return ["Action: Knock", "Action: Done"]
    elif state["phase"] == "Layoff":
        return ["Action: Done"]
    else:
        return []

# Get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    player_0_obs = {
        "deadwood": state["player_0_deadwood"],
        "melds": state["player_0_melds"],
        "card_grid": state["dealer_hand"]
    }
    player_1_obs = {
        "deadwood": state["player_1_deadwood"],
        "melds": state["player_1_melds"],
        "card_grid": state["dealer_hand"]
    }
    return [player_0_obs, player_1_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # This function would need to be implemented based on the specific game logic
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ["Action: 7c", "Action: 8c", "Action: 9c", "Action: Tc", "Action: Knock"]
    else:
        return ["Action: 9d", "Action: Td", "Action: Jd", "Action: Qd", "Action: Knock"]

# Example usage
if __name__ == "__main__":
    state = get_initial_state()
    print("Initial State:", state)
    state = apply_action(state, "Draw stock")
    print("After Draw stock:", state)
    state = apply_action(state, "Action: 7c")
    print("After Action: 7c:", state)
    state = apply_action(state, "Action: 8c")
    print("After Action: 8c:", state)
    state = apply_action(state, "Action: 9c")
    print("After Action: 9c:", state)
    state = apply_action(state, "Action: Tc")
    print("After Action: Tc:", state)
    state = apply_action(state, "Action: Knock")
    print("After Knock:", state)
    print("Legal Actions:", get_legal_actions(state))
    print("Observations:", get_observations(state))