import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial state setup
    state = {
        "deck": ["2c", "2d", "2h", "2s", "3c", "3d", "3h", "3s", "4c", "4d", "4h", "4s",
                 "5c", "5d", "5h", "5s", "6c", "6d", "6h", "6s", "7c", "7d", "7h", "7s",
                 "8c", "8d", "8h", "8s", "9c", "9d", "9h", "9s", "10c", "10d", "10h", "10s",
                 "Ac", "Ad", "Ah", "As", "2c", "2d", "2h", "2s", "3c", "3d", "3h", "3s",
                 "4c", "4d", "4h", "4s", "5c", "5d", "5h", "5s", "6c", "6d", "6h", "6s",
                 "7c", "7d", "7h", "7s", "8c", "8d", "8h", "8s", "9c", "9d", "9h", "9s",
                 "10c", "10d", "10h", "10s", "Ac", "Ad", "Ah", "As"],
        "discard_pile": [],
        "upcard": None,
        "knock_card": None,
        "deadwood": {"player_0": [], "player_1": []},
        "melds": {"player_0": {}, "player_1": {}},
        "phase": "Draw",
        "current_player": 0,
        "round_number": 1,
        "wall": None,
        "drawn_cards": []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    
    if action == "Draw stock":
        new_state["drawn_cards"].append(new_state["deck"].pop())
        new_state["phase"] = "Discard"
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
        return new_state
    
    if action == "Draw upcard":
        new_state["drawn_cards"].append(new_state["discard_pile"].pop())
        new_state["phase"] = "Discard"
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
        return new_state
    
    if action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        new_state["discard_pile"].append(card_to_discard)
        new_state["drawn_cards"].append(new_state["deck"].pop())
        new_state["phase"] = "Knock"
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
        return new_state
    
    if action == "Action: Knock":
        new_state["knock_card"] = sum([sum(rank_values.values()) for rank_values in new_state["deadwood"].values()])
        new_state["phase"] = "Layoff"
        return new_state
    
    if action == "Action: Done":
        new_state["phase"] = "Layoff"
        return new_state
    
    if action == "Pass":
        new_state["phase"] = "Layoff"
        return new_state
    
    raise ValueError(f"Invalid action: {action}")

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["phase"] == "Wall":
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"player_{player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["phase"] == "Wall":
        return [0.0, 0.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["phase"] == "Wall":
        return []
    if state["phase"] == "Knock":
        return ["Action: Done"]
    if state["phase"] == "Layoff":
        return ["Action: Done"]
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    if state["phase"] == "Discard":
        return ["Action: " + card for card in state["deck"]]
    return []

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        "deck": state["deck"],
        "discard_pile": state["discard_pile"],
        "upcard": state["upcard"],
        "knock_card": state["knock_card"],
        "deadwood": state["deadwood"]["player_0"],
        "melds": state["melds"]["player_0"],
        "phase": state["phase"],
        "current_player": state["current_player"],
        "round_number": state["round_number"],
        "wall": state["wall"],
        "drawn_cards": state["drawn_cards"]
    }
    player_1_obs = {
        "deck": state["deck"],
        "discard_pile": state["discard_pile"],
        "upcard": state["upcard"],
        "knock_card": state["knock_card"],
        "deadwood": state["deadwood"]["player_1"],
        "melds": state["melds"]["player_1"],
        "phase": state["phase"],
        "current_player": state["current_player"],
        "round_number": state["round_number"],
        "wall": state["wall"],
        "drawn_cards": state["drawn_cards"]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we'll just randomly select actions from the legal actions
    legal_actions = get_legal_actions(resample_history.get_current_state(obs_action_history))
    return [random.choice(legal_actions) for _ in obs_action_history]