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

# Helper function to generate a shuffled deck
def shuffle_deck() -> list[int]:
    deck = list(range(1, 53))
    random.shuffle(deck)
    return deck

# Initial state of the game
def get_initial_state() -> State:
    # Initialize the deck
    deck = shuffle_deck()
    # Shuffle the deck and deal cards to each player
    dealer_cards = deck[:26]
    upcard = deck[26]
    stockpile = deck[27:]
    
    # Create the initial state
    state = {
        "deck": deck,
        "dealer_cards": dealer_cards,
        "upcard": upcard,
        "stockpile": stockpile,
        "current_player": 0,
        "knocked": False,
        "knock_card": 10,
        "deadwood": {},
        "melds": {}
    }
    return state

# Apply an action to the game state
def apply_action(state: State, action: Action) -> State:
    if action == "Draw stock":
        state["stockpile"].append(state["upcard"])
        state["upcard"] = state["stockpile"].pop()
        state["current_player"] = 1 if state["current_player"] == 0 else 0
    elif action == "Draw upcard":
        state["dealer_cards"].append(state["upcard"])
        state["upcard"] = state["stockpile"].pop()
        state["current_player"] = 1 if state["current_player"] == 0 else 0
    elif action.startswith("Action: "):
        card = int(action.split(":")[1])
        state["dealer_cards"].remove(card)
        state["current_player"] = 1 if state["current_player"] == 0 else 0
    elif action == "Knock":
        state["knocked"] = True
        state["knock_card"] = 10
    elif action == "Done":
        state["knocked"] = True
        state["knock_card"] = 10
    elif action == "Pass":
        state["knocked"] = True
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
def get_rewards(state: State) -> list[float]:
    if state["knocked"]:
        return [0.0, 0.0]  # No rewards yet
    return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    current_player = get_current_player(state)
    if state["knocked"]:
        return ["Done"]
    if state["knocked"] and state["knock_card"] <= state["deadwood"][current_player]:
        return ["Knock"]
    if state["current_player"] == 0:
        return ["Draw stock", "Draw upcard"]
    else:
        return ["Draw stock", "Draw upcard", "Action: 2c", "Action: 3d", "Action: 4h", "Action: 5s", "Action: 6c", "Action: 7h", "Action: 8d", "Action: 9t", "Action: Ac", "Action: 2s", "Action: 3s", "Action: 4s", "Action: 5s", "Action: 6s", "Action: 7s", "Action: 8s", "Action: 9s", "Action: Tc", "Action: Ts", "Action: 9c", "Action: 8c", "Action: 7c", "Action: 6c", "Action: 5c", "Action: 4c", "Action: 3c", "Action: 2c", "Action: 10c", "Action: Jc", "Action: Qc", "Action: Kc", "Action: 10s", "Action: Js", "Action: Qs", "Action: Ks", "Action: 10h", "Action: Jh", "Action: Qh", "Action: Kh", "Action: 10d", "Action: Jd", "Action: Qd", "Action: Kd", "Action: Done"]
    else:
        return ["Draw stock", "Draw upcard", "Action: 2c", "Action: 3d", "Action: 4h", "Action: 5s", "Action: 6c", "Action: 7h", "Action: 8d", "Action: 9t", "Action: Ac", "Action: 2s", "Action: 3s", "Action: 4s", "Action: 5s", "Action: 6s", "Action: 7s", "Action: 8s", "Action: 9s", "Action: Tc", "Action: Ts", "Action: 9c", "Action: 8c", "Action: 7c", "Action: 6c", "Action: 5c", "Action: 4c", "Action: 3c", "Action: 2c", "Action: 10c", "Action: Jc", "Action: Qc", "Action: Kc", "Action: 10s", "Action: Js", "Action: Qs", "Action: Ks", "Action: 10h", "Action: Jh", "Action: Qh", "Action: Kh", "Action: 10d", "Action: Jd", "Action: Qd", "Action: Kd", "Action: Done"]

# Get the observations for the current state
def get_observations(state: State) -> list[PlayerObservation]:
    current_player = get_current_player(state)
    deadwood = state["deadwood"][current_player]
    melds = state["melds"][current_player]
    return [
        {
            "deadwood": deadwood,
            "melds": melds
        },
        {
            "deadwood": state["deadwood"][1 - current_player],
            "melds": state["melds"][1 - current_player]
        }
    ]

# Resample history
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # For simplicity, we'll just randomly select actions from the legal ones
    legal_actions = get_legal_actions(resample_history.get_initial_state())
    return [random.choice(legal_actions) for _ in obs_action_history]