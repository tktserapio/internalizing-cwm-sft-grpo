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
    deck = list(range(1, 53))  # 1-13 for each suit (Ace through King)
    random.shuffle(deck)
    # Deal the cards
    dealer_hand = deck[:26]
    non_dealer_hand = deck[26:]
    # Create the state dictionary
    state = {
        "dealer_hand": dealer_hand,
        "non_dealer_hand": non_dealer_hand,
        "upcard": None,
        "knocked": False,
        "knock_card_value": 10,
        "deadwood": 0,
        "melds": [],
        "phase": "Draw",
        "stockpile": deck[26:]  # Remaining cards in the stockpile
    }
    return state

# Apply an action to the game state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == "Draw stock":
        new_state["stockpile"].pop(0)
        new_state["upcard"] = new_state["stockpile"][0]
        new_state["phase"] = "Discard"
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["stockpile"].pop(0)
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card_to_discard = int(action.split(":")[1])
        new_state["dealer_hand"].remove(card_to_discard)
        new_state["stockpile"].append(card_to_discard)
        new_state["phase"] = "Knock"
    elif action == "Knock":
        new_state["knocked"] = True
        new_state["melds"], new_state["deadwood"] = organize_melds(new_state["dealer_hand"])
        new_state["phase"] = "Layoff"
    elif action == "Done":
        new_state["phase"] = "Layoff"
    elif action == "Pass":
        new_state["phase"] = "Layoff"
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

# Organize melds and calculate deadwood
def organize_melds(hand: List[int]) -> tuple[List[List[int]], int]:
    melds = []
    deadwood = 0
    for card in sorted(hand, reverse=True):
        if len(melds) == 0 or melds[-1][-1] + 1 == card:
            melds[-1].append(card)
        else:
            melds.append([card])
        if len(melds[-1]) < 3:
            deadwood += card
    return melds, deadwood

# Get the current player
def get_current_player(state: State) -> int:
    return 0 if state["phase"] == "Draw" else 1

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards
def get_rewards(state: State) -> List[float]:
    if state["knocked"]:
        return [0.0, 0.0]  # No immediate rewards until layoff
    else:
        return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> List[Action]:
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Knock":
        return ["Action: " + str(card) for card in state["dealer_hand"]]
    elif state["phase"] == "Layoff":
        return []
    else:
        return []

# Get observations
def get_observations(state: State) -> List[PlayerObservation]:
    dealer_obs = {
        "dealer_hand": state["dealer_hand"],
        "upcard": state["upcard"],
        "deadwood": state["deadwood"],
        "melds": state["melds"]
    }
    non_dealer_obs = {
        "non_dealer_hand": state["non_dealer_hand"],
        "upcard": state["upcard"],
        "deadwood": state["deadwood"],
        "melds": state["melds"]
    }
    return [dealer_obs, non_dealer_obs]

# Resample history
def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # For simplicity, we'll just return a fixed sequence of actions
    # This should be replaced with actual resampling logic
    if player_id == 0:
        return ["Draw stock", "Action: 2c", "Knock"]
    else:
        return ["Draw stock", "Action: 2d", "Knock"]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print(initial_state)
    # Simulate a simple game flow
    state = apply_action(initial_state, "Draw stock")
    state = apply_action(state, "Action: 2c")
    state = apply_action(state, "Knock")
    print(state)