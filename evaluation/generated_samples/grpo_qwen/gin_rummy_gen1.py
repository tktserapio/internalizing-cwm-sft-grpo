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

# Helper function to generate a shuffled deck
def shuffle_deck() -> List[int]:
    deck = list(range(1, 53))
    random.shuffle(deck)
    return deck

# Initial state generation
def get_initial_state() -> State:
    # Shuffle the deck
    deck = shuffle_deck()
    # Deal the first two cards to each player
    upcard = deck.pop(0)
    stockpile = deck
    # Initialize state
    state = {
        "deck": deck,
        "upcard": upcard,
        "stockpile": stockpile,
        "phase": "Draw",
        "player_0_hand": [],
        "player_1_hand": [],
        "player_0_melds": [],
        "player_1_melds": [],
        "player_0_deadwood": 0,
        "player_1_deadwood": 0,
        "knocked_by": -1,
        "knock_value": 0,
        "knock_phase": False
    }
    # Deal cards to players
    for _ in range(7):
        state["player_0_hand"].append(upcard)
        state["player_1_hand"].append(deck.pop(0))
    return state

# Apply action to the state
def apply_action(state: State, action: Action) -> State:
    if action == "Draw stock":
        state["stockpile"].append(state["upcard"])
        state["upcard"] = state["stockpile"].pop(0)
        state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card_to_discard = int(action.split(":")[1])
        state["player_0_hand"].remove(card_to_discard)
        state["player_1_hand"].remove(card_to_discard)
        state["player_0_deadwood"] += card_to_discard // 10 + 1
        state["player_1_deadwood"] += card_to_discard // 10 + 1
        state["phase"] = "Knock"
    elif action == "Knock":
        state["knocked_by"] = get_current_player(state)
        state["knock_value"] = state["player_" + str(state["knocked_by"]) + "_deadwood"]
        state["knock_phase"] = True
    elif action == "Done":
        state["knock_phase"] = False
    elif action == "Pass":
        state["phase"] = "Draw"
    else:
        raise ValueError(f"Invalid action: {action}")
    return state

# Get current player
def get_current_player(state: State) -> int:
    return state["knocked_by"]

# Get player name
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards
def get_rewards(state: State) -> List[float]:
    if state["knock_phase"]:
        return [state["knock_value"], 0.0]
    return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> List[Action]:
    if state["knock_phase"]:
        return ["Action: Done"]
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    if state["knock_phase"]:
        return []
    return ["Action: 2c", "Action: 3d", "Action: 4s", "Action: 5h", "Action: 6s", "Action: 7c", "Action: 8d", "Action: 9h", "Action: Tc", "Action: Jd", "Action: Qs", "Action: Kd", "Action: Ah", "Action: 2d", "Action: 3s", "Action: 4h", "Action: 5d", "Action: 6c", "Action: 7d", "Action: 8s", "Action: 9t", "Action: Td", "Action: Jc", "Action: Qd", "Action: Ks", "Action: Ak", "Draw stock", "Draw upcard", "Action: Knock", "Pass"]

# Get observations
def get_observations(state: State) -> List[PlayerObservation]:
    player_0_obs = {
        "deck": state["deck"],
        "upcard": state["upcard"],
        "stockpile": state["stockpile"],
        "phase": state["phase"],
        "hand": state["player_0_hand"],
        "melds": state["player_0_melds"],
        "deadwood": state["player_0_deadwood"]
    }
    player_1_obs = {
        "deck": state["deck"],
        "upcard": state["upcard"],
        "stockpile": state["stockpile"],
        "phase": state["phase"],
        "hand": state["player_1_hand"],
        "melds": state["player_1_melds"],
        "deadwood": state["player_1_deadwood"]
    }
    return [player_0_obs, player_1_obs]

# Resample history
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # For simplicity, we'll just randomly select an action from the legal actions
    legal_actions = get_legal_actions(resample_history.get_initial_state())
    return [random.choice(legal_actions)]