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

def get_initial_state() -> State:
    # Initial state setup
    state = {
        "deck": list(range(1, 53)),  # Full deck excluding jokers
        "upcard": None,              # Upcard for the first turn
        "dealer": 0,                 # Dealer starts as player 0
        "phase": "Draw",             # Initial phase is Draw
        "knock_card": 10,            # Default knock card value
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
        "wall": []                  # Stock pile
    }
    return state

def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == "Draw stock":
        new_state["wall"].append(new_state["deck"].pop())
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["deck"].pop()
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        if card_to_discard in new_state["player_0_hand"]:
            new_state["player_0_hand"].remove(card_to_discard)
            if card_to_discard in new_state["player_0_melds"]:
                new_state["player_0_melds"].remove(card_to_discard)
            new_state["player_0_deadwood"] += card_to_discard_to_value(card_to_discard)
        else:
            new_state["player_1_hand"].remove(card_to_discard)
            if card_to_discard in new_state["player_1_melds"]:
                new_state["player_1_melds"].remove(card_to_discard)
            new_state["player_1_deadwood"] += card_to_discard_to_value(card_to_discard)
        new_state["wall"].append(new_state["deck"].pop())
    elif action == "Action: Knock":
        new_state["phase"] = "Knock"
        new_state["knock_card"] = new_state["wall"][0]
        new_state["knock_card_value"] = card_to_value(new_state["knock_card"])
        new_state["player_0_meld_count"] = len(new_state["player_0_melds"])
        new_state["player_1_meld_count"] = len(new_state["player_1_melds"])
        new_state["player_0_deadwood"] = sum(card_to_value(card) for card in new_state["player_0_deadwood"])
        new_state["player_1_deadwood"] = sum(card_to_value(card) for card in new_state["player_1_deadwood"])
        if new_state["player_0_deadwood"] <= new_state["knock_card_value"]:
            new_state["phase"] = "Layoff"
            new_state["player_0_melds"] = []
            new_state["player_1_melds"] = []
            new_state["player_0_deadwood"] = 0
            new_state["player_1_deadwood"] = 0
        else:
            new_state["phase"] = "Done"
    elif action == "Pass":
        if new_state["phase"] == "Draw":
            new_state["phase"] = "Discard"
        else:
            new_state["phase"] = "Wall"
    elif action == "Deal:1,2,3,...":
        # Deal cards to players
        pass
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def card_to_value(card: str) -> int:
    # Convert card to its value
    ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 1}
    suits = {'S': 0, 'C': 1, 'D': 2, 'H': 3}
    return ranks[card[-1]] + suits[card[:-1]]

def card_to_discard_value(card: str) -> int:
    # Convert card to its value for deadwood calculation
    return card_to_value(card)

def get_current_player(state: State) -> int:
    # Determine the current player based on the dealer and phase
    if state["phase"] == "Draw":
        return state["dealer"]
    else:
        return (state["dealer"] + 1) % 2

def get_player_name(player_id: int) -> str:
    # Return the name of the player
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    # Calculate rewards based on the game rules
    if state["phase"] == "Wall":
        return [0.0, 0.0]
    elif state["phase"] == "Done":
        if state["player_0_meld_count"] > state["player_1_meld_count"]:
            return [state["player_0_deadwood"], -state["player_1_deadwood"]]
        elif state["player_0_meld_count"] < state["player_1_meld_count"]:
            return [-state["player_0_deadwood"], state["player_1_deadwood"]]
        else:
            return [state["player_0_deadwood"] + 25, -state["player_1_deadwood"] + 25]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    # Get legal actions based on the current state
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Discard":
        if state["player_0_hand"]:
            return ["Action: " + card for card in state["player_0_hand"]] + ["Action: Knock"]
        else:
            return ["Pass"]
    elif state["phase"] == "Knock":
        return ["Action: " + card for card in state["player_0_melds"] + state["player_0_hand"]] + ["Action: Done"]
    elif state["phase"] == "Layoff":
        return ["Action: " + card for card in state["player_0_melds"] + state["player_0_hand"]] + ["Action: Done"]
    elif state["phase"] == "Wall":
        return ["Pass"]

def get_observations(state: State) -> List[PlayerObservation]:
    # Get observations for each player
    player_0_obs = {
        "upcard": state["upcard"],
        "wall": state["wall"],
        "dealer": state["dealer"],
        "player_0_hand": state["player_0_hand"],
        "player_0_deadwood": state["player_0_deadwood"],
        "player_0_melds": state["player_0_melds"],
        "player_0_meld_count": state["player_0_meld_count"],
        "player_0_score": state["player_0_score"],
        "player_1_hand": state["player_1_hand"],
        "player_1_deadwood": state["player_1_deadwood"],
        "player_1_melds": state["player_1_melds"],
        "player_1_meld_count": state["player_1_meld_count"],
        "player_1_score": state["player_1_score"],
        "phase": state["phase"],
        "knock_card": state["knock_card"],
        "knock_card_value": state["knock_card_value"]
    }
    player_1_obs = {
        "upcard": state["upcard"],
        "wall": state["wall"],
        "dealer": (state["dealer"] + 1) % 2,
        "player_1_hand": state["player_1_hand"],
        "player_1_deadwood": state["player_1_deadwood"],
        "player_1_melds": state["player_1_melds"],
        "player_1_meld_count": state["player_1_meld_count"],
        "player_1_score": state["player_1_score"],
        "player_0_hand": state["player_0_hand"],
        "player_0_deadwood": state["player_0_deadwood"],
        "player_0_melds": state["player_0_melds"],
        "player_0_meld_count": state["player_0_meld_count"],
        "player_0_score": state["player_0_score"],
        "phase": state["phase"],
        "knock_card": state["knock_card"],
        "knock_card_value": state["knock_card_value"]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Sample a valid sequence of actions
    # For simplicity, we assume a deterministic history that leads to a specific outcome
    # In a real implementation, this would involve stochastic sampling
    if player_id == 0:
        return ["Draw stock", "Action: 3d", "Action: 7c8c9cTc", "Action: Knock"]
    else:
        return ["Draw stock", "Action: 3d", "Action: 7c8c9cTc", "Action: Knock"]