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
    # Initialize the deck and shuffle it
    deck = list(range(1, 53))  # 1-13 for each suit
    random.shuffle(deck)
    
    # Deal the cards
    dealer_hand = deck[:26]
    non_dealer_hand = deck[26:]
    
    # Set up the state
    state = {
        "dealer_hand": dealer_hand,
        "non_dealer_hand": non_dealer_hand,
        "upcard": None,
        "knock_card": 10,  # Default knock card value
        "phase": "Draw",
        "current_player": 0,
        "wall": [],
        "deadwood": {
            "player_0": 0,
            "player_1": 0
        }
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    if action == "Draw stock":
        if len(state["wall"]) > 1:
            state["wall"].pop()
            state["wall"].pop()
        else:
            raise ValueError("Stock pile exhausted")
    elif action == "Draw upcard":
        if state["upcard"] is None:
            state["upcard"] = state["wall"].pop()
        else:
            raise ValueError("Upcard already drawn")
    elif action.startswith("Action: "):
        card_to_discard = action[8:]  # Remove "Action:" prefix
        if card_to_discard in state["dealer_hand"]:
            state["dealer_hand"].remove(card_to_discard)
        elif card_to_discard in state["non_dealer_hand"]:
            state["non_dealer_hand"].remove(card_to_discard)
        else:
            raise ValueError(f"Invalid card to discard: {card_to_discard}")
    elif action == "Action: Knock":
        if state["current_player"] == 0:
            player = "player_0"
        else:
            player = "player_1"
        
        # Calculate deadwood
        state[player]["deadwood"] = sum([10 if card <= 10 else 1 if card <= 11 else 0 for card in state[player]["hand"]])
        
        # Check if knock is valid
        if state[player]["deadwood"] <= state["knock_card"]:
            state["phase"] = "Knock"
            state["current_player"] = 1 - state["current_player"]
        else:
            raise ValueError(f"Invalid knock: {state[player]['deadwood']} > {state['knock_card']}")
    elif action == "Action: Done":
        state["phase"] = "Discard"
        state["current_player"] = 1 - state["current_player"]
    elif action == "Pass":
        if state["phase"] == "Draw":
            state["phase"] = "Discard"
            state["current_player"] = 1 - state["current_player"]
        else:
            raise ValueError("Cannot pass during Knock phase")
    else:
        raise ValueError(f"Unknown action: {action}")
    
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state["current_player"]

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards
def get_rewards(state: State) -> List[float]:
    if state["phase"] == "Wall":
        return [0.0, 0.0]
    else:
        return [state["deadwood"]["player_0"], state["deadwood"]["player_1"]]

# Get legal actions
def get_legal_actions(state: State) -> List[Action]:
    if state["phase"] == "Wall":
        return []
    elif state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Knock":
        if state["current_player"] == 0:
            player = "player_0"
        else:
            player = "player_1"
        return ["Action: Knock", "Action: Done"]
    elif state["phase"] == "Discard":
        if state["current_player"] == 0:
            player = "player_0"
        else:
            player = "player_1"
        return ["Action: " + card for card in state[player]["hand"]] + ["Action: Knock"]
    else:
        raise ValueError(f"Unknown phase: {state['phase']}")

# Get observations
def get_observations(state: State) -> List[PlayerObservation]:
    observations = []
    for player_id in range(2):
        player = "player_" + str(player_id)
        hand = state[player]["hand"]
        deadwood = state[player]["deadwood"]
        melds = state[player]["melds"]
        observations.append({
            "hand": hand,
            "deadwood": deadwood,
            "melds": melds
        })
    return observations

# Resample history
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # For simplicity, we'll just randomly select actions from the possible ones
    # This should be replaced with a more sophisticated resampling mechanism
    possible_actions = get_legal_actions(resample_history.get_observations())
    return [random.choice(possible_actions) for _ in obs_action_history]

# Example usage
initial_state = get_initial_state()
print("Initial State:", initial_state)

# Simulate a simple round
state = initial_state
state = apply_action(state, "Draw upcard")
state = apply_action(state, "Action: 4c")
state = apply_action(state, "Action: Knock")
print("After Knock:", state)

# Resample history
obs_action_history = [(resample_history.get_observations(), None)]
resampled_actions = resample_history(obs_action_history, 0)
print("Resampled Actions:", resampled_actions)