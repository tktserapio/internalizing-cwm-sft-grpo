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

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initial state setup
    state = {
        "deck": list(range(1, 53)),  # Full deck of cards
        "upcard": None,              # Upcard (None if no upcard)
        "dealer": 0,                 # Dealer index (0 or 1)
        "knock_card": 10,            # Knock card value
        "phase": "Draw",             # Current phase: Draw or Knock
        "player_0_hand": [],         # Player 0's hand
        "player_1_hand": [],         # Player 1's hand
        "player_0_deadwood": 0,      # Player 0's deadwood
        "player_1_deadwood": 0,      # Player 1's deadwood
        "player_0_melds": [],        # Player 0's melds
        "player_1_melds": []         # Player 1's melds
    }
    # Shuffle the deck
    random.shuffle(state["deck"])
    return state

# Apply an action to the current state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == "Draw stock":
        new_state["upcard"] = new_state["deck"].pop()
        new_state["phase"] = "Discard"
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["deck"].pop()
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        new_state["player_0_hand"].remove(card_to_discard)
        new_state["player_1_hand"].remove(card_to_discard)
        new_state["player_0_deadwood"] += get_card_value(card_to_discard)
        new_state["player_1_deadwood"] += get_card_value(card_to_discard)
        new_state["phase"] = "Knock"
    elif action == "Action: Knock":
        new_state["phase"] = "Layoff"
        new_state["knock_card"] = get_card_value(new_state["upcard"])
        new_state["player_0_melds"], new_state["player_1_melds"], new_state["player_0_deadwood"], new_state["player_1_deadwood"] = lay_off(new_state)
    elif action == "Action: Done":
        new_state["phase"] = "Done"
    elif action == "Pass":
        new_state["phase"] = "Done"
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state["dealer"]

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    if state["phase"] == "Done":
        return [state["player_0_deadwood"], state["player_1_deadwood"]]
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Knock":
        return ["Action: Knock", "Action: Done"]
    elif state["phase"] == "Layoff":
        return ["Action: Done"]
    elif state["phase"] == "Wall":
        return []
    else:
        raise ValueError("Invalid phase")

# Get observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    player_0_obs = {
        "deadwood": state["player_0_deadwood"],
        "melds": state["player_0_melds"],
        "hand": state["player_0_hand"],
        "upcard": state["upcard"],
        "dealer": state["dealer"]
    }
    player_1_obs = {
        "deadwood": state["player_1_deadwood"],
        "melds": state["player_1_melds"],
        "hand": state["player_1_hand"],
        "upcard": state["upcard"],
        "dealer": state["dealer"]
    }
    return [player_0_obs, player_1_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Placeholder for resampling logic
    # For simplicity, we randomly select actions based on the current phase
    if obs_action_history[-1][1] is None:
        if player_id == 0:
            return ["Draw stock", "Draw upcard", "Action: 2h", "Action: Knock"]
        else:
            return ["Draw stock", "Draw upcard", "Action: 2h", "Action: Knock"]
    else:
        return []

# Helper function to get the value of a card
def get_card_value(card: str) -> int:
    rank = int(card[1:])
    if card[0] in "Ac":
        return 10
    elif card[0] in "JQK":
        return 10
    else:
        return rank

# Helper function to lay off deadwood
def lay_off(state: State) -> tuple[List[List[str]], List[List[str]], int, int]:
    player_0_melds = state["player_0_melds"]
    player_1_melds = state["player_1_melds"]
    player_0_deadwood = state["player_0_deadwood"]
    player_1_deadwood = state["player_1_deadwood"]
    
    # Lay off deadwood from player 1 onto player 0's melds
    for meld in player_1_melds:
        for card in meld:
            if card in player_0_deadwood:
                player_0_deadwood.remove(card)
                player_1_deadwood -= get_card_value(card)
    
    # Lay off deadwood from player 0 onto player 1's melds
    for meld in player_0_melds:
        for card in meld:
            if card in player_1_deadwood:
                player_1_deadwood.remove(card)
                player_0_deadwood -= get_card_value(card)
    
    return player_0_melds, player_1_melds, player_0_deadwood, player_1_deadwood

# Example usage
if __name__ == "__main__":
    state = get_initial_state()
    print("Initial State:", state)
    state = apply_action(state, "Draw stock")
    print("After Draw stock:", state)
    state = apply_action(state, "Action: 2h")
    print("After Action: 2h:", state)
    state = apply_action(state, "Action: Knock")
    print("After Knock:", state)