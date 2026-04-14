import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Dict, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the state
def get_initial_state() -> State:
    # Initial state setup
    state = {
        "deck": [str(i) + s for i in range(1, 14) for s in ['S', 'C', 'D', 'H']],
        "upcard": None,
        "dealer": 0,
        "knock_card": 10,
        "phase": "Draw",
        "player_0_hand": [],
        "player_1_hand": [],
        "player_0_deadwood": 0,
        "player_1_deadwood": 0,
        "player_0_melds": [],
        "player_1_melds": [],
        "player_0_meld_count": 0,
        "player_1_meld_count": 0,
        "player_0_score": 0,
        "player_1_score": 0,
        "player_0_turn": True,
        "player_1_turn": False,
        "wall": []
    }
    return state

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == "Draw stock":
        new_state["upcard"] = new_state["deck"].pop()
        new_state["phase"] = "Discard"
        new_state["player_0_turn"] = not new_state["player_0_turn"]
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["deck"].pop()
        new_state["phase"] = "Discard"
        new_state["player_0_turn"] = not new_state["player_0_turn"]
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        new_state["player_0_hand"].remove(card_to_discard)
        new_state["wall"].append(card_to_discard)
        new_state["phase"] = "Knock"
        new_state["player_0_turn"] = not new_state["player_0_turn"]
    elif action == "Action: Knock":
        new_state["knock_card"] = new_state["player_0_deadwood"]
        new_state["phase"] = "Layoff"
        new_state["player_0_turn"] = not new_state["player_0_turn"]
    elif action == "Action: Done":
        new_state["phase"] = "Draw"
        new_state["player_0_turn"] = not new_state["player_0_turn"]
    elif action == "Pass":
        new_state["phase"] = "Draw"
        new_state["player_0_turn"] = not new_state["player_0_turn"]
    return new_state

# Function to determine the current player
def get_current_player(state: State) -> int:
    return 0 if state["player_0_turn"] else 1

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Function to get the rewards for the current state
def get_rewards(state: State) -> List[float]:
    if state["phase"] == "Wall":
        return [0.0, 0.0]
    return [state["player_0_score"], state["player_1_score"]]

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state["phase"] == "Wall":
        return []
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    if state["phase"] == "Knock":
        return ["Action: Knock", "Action: Done"]
    if state["phase"] == "Layoff":
        return ["Action: Done"]
    return []

# Function to get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    player_0_obs = {
        "deadwood": state["player_0_deadwood"],
        "melds": state["player_0_melds"],
        "wall": state["wall"],
        "upcard": state["upcard"],
        "phase": state["phase"],
        "player_id": 0
    }
    player_1_obs = {
        "deadwood": state["player_1_deadwood"],
        "melds": state["player_1_melds"],
        "wall": state["wall"],
        "upcard": state["upcard"],
        "phase": state["phase"],
        "player_id": 1
    }
    return [player_0_obs, player_1_obs]

# Function to resample history
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Placeholder for resampling logic
    # For simplicity, we'll just return a random action from the legal actions
    legal_actions = get_legal_actions(resample_history.observation)
    return [legal_actions[0]]  # Randomly select an action from the legal actions

# Example usage
if __name__ == "__main__":
    # Initialize the game state
    state = get_initial_state()
    
    # Apply actions to simulate the game flow
    state = apply_action(state, "Draw stock")
    state = apply_action(state, "Action: 3d")
    state = apply_action(state, "Action: 7c8c9cTc")
    state = apply_action(state, "Action: Knock")
    state = apply_action(state, "Action: Done")
    
    # Get the current player and their name
    current_player = get_current_player(state)
    player_name = get_player_name(current_player)
    
    # Get the legal actions for the current player
    legal_actions = get_legal_actions(state)
    
    # Get the observations for both players
    observations = get_observations(state)
    
    # Resample history to generate a sequence of actions
    resampled_actions = resample_history([], current_player)
    
    print(f"Current Player: {player_name}")
    print(f"Legal Actions: {legal_actions}")
    print(f"Observations: {observations}")
    print(f"Resampled Actions: {resampled_actions}")