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
    upcard = deck[26]
    stockpile = deck[27:]
    
    return {
        "dealer_hand": dealer_hand,
        "upcard": upcard,
        "stockpile": stockpile,
        "knocked": False,
        "knock_card": None,
        "round_number": 1,
        "current_player": 0,
        "phase": "Draw",
        "deadwood": {0: 0, 1: 0},
        "melds": {0: [], 1: []}
    }

# Apply an action to the game state
def apply_action(state: State, action: Action) -> State:
    if action == "Draw stock":
        state["stockpile"].append(state["upcard"])
        state["upcard"] = state["stockpile"].pop()
        state["phase"] = "Discard"
        state["current_player"] = (state["current_player"] + 1) % 2
    elif action == "Draw upcard":
        state["stockpile"].append(state["upcard"])
        state["upcard"] = state["stockpile"].pop()
        state["phase"] = "Discard"
        state["current_player"] = (state["current_player"] + 1) % 2
    elif action.startswith("Action: "):
        card_to_discard = int(action.split(":")[1])
        state["dealer_hand"].remove(card_to_discard)
        state["stockpile"].append(card_to_discard)
        state["upcard"] = state["stockpile"].pop()
        state["phase"] = "Discard"
        state["current_player"] = (state["current_player"] + 1) % 2
    elif action == "Action: Knock":
        state["knocked"] = True
        state["knock_card"] = state["upcard"]
        state["phase"] = "Layoff"
    elif action == "Action: Done":
        state["phase"] = "Layoff"
    elif action == "Pass":
        state["phase"] = "Layoff"
    else:
        raise ValueError(f"Invalid action: {action}")
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state["current_player"]

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    if state["knocked"]:
        return [0.0, 0.0]  # No rewards yet, waiting for layoff
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Discard":
        return ["Action: " + str(card) for card in state["dealer_hand"]]
    elif state["phase"] == "Layoff":
        return []
    else:
        raise ValueError("Invalid phase")

# Get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    dealer_hand = state["dealer_hand"]
    upcard = state["upcard"]
    stockpile = state["stockpile"]
    deadwood = state["deadwood"]
    melds = state["melds"]
    current_player = get_current_player(state)
    player_0_obs = {
        "dealer_hand": dealer_hand,
        "upcard": upcard,
        "stockpile": stockpile,
        "knocked": state["knocked"],
        "knock_card": state["knock_card"],
        "round_number": state["round_number"],
        "current_player": current_player,
        "phase": state["phase"],
        "deadwood": deadwood[current_player],
        "melds": melds[current_player]
    }
    player_1_obs = {
        "dealer_hand": dealer_hand,
        "upcard": upcard,
        "stockpile": stockpile,
        "knocked": state["knocked"],
        "knock_card": state["knock_card"],
        "round_number": state["round_number"],
        "current_player": 1 - current_player,
        "phase": state["phase"],
        "deadwood": deadwood[1 - current_player],
        "melds": melds[1 - current_player]
    }
    return [player_0_obs, player_1_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This is a placeholder function for demonstration purposes
    # In a real implementation, this would involve sampling valid sequences based on the observed history
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ["Draw stock", "Action: 2c", "Action: 3c", "Action: 4c", "Action: 5c", "Action: 6c", "Action: 7c", "Action: 8c", "Action: 9c", "Action: 10c", "Action: Jc", "Action: Qc", "Action: Ac", "Action: 2d", "Action: 3d", "Action: 4d", "Action: 5d", "Action: 6d", "Action: 7d", "Action: 8d", "Action: 9d", "Action: 10d", "Action: Jd", "Action: Qd", "Action: Ad", "Action: 2h", "Action: 3h", "Action: 4h", "Action: 5h", "Action: 6h", "Action: 7h", "Action: 8h", "Action: 9h", "Action: 10h", "Action: Jh", "Action: Qh", "Action: Ah", "Action: 2s", "Action: 3s", "Action: 4s", "Action: 5s", "Action: 6s", "Action: 7s", "Action: 8s", "Action: 9s", "Action: 10s", "Action: Js", "Action: Qs", "Action: As", "Action: Knock"]
    else:
        return ["Draw stock", "Action: 2c", "Action: 3c", "Action: 4c", "Action: 5c", "Action: 6c", "Action: 7c", "Action: 8c", "Action: 9c", "Action: 10c", "Action: Jc", "Action: Qc", "Action: Ac", "Action: 2d", "Action: 3d", "Action: 4d", "Action: 5d", "Action: 6d", "Action: 7d", "Action: 8d", "Action: 9d", "Action: 10d", "Action: Jd", "Action: Qd", "Action: Ad", "Action: 2h", "Action: 3h", "Action: 4h", "Action: 5h", "Action: 6h", "Action: 7h", "Action: 8h", "Action: 9h", "Action: 10h", "Action: Jh", "Action: Qh", "Action: Ah", "Action: 2s", "Action: 3s", "Action: 4s", "Action: 5s", "Action: 6s", "Action: 7s", "Action: 8s", "Action: 9s", "Action: 10s", "Action: Js", "Action: Qs", "Action: As", "Action: Knock"]