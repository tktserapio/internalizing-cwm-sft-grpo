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
    """Returns the initial game state before any actions are taken."""
    # Initial state setup
    state = {
        "deck": ["Ah", "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th", "Jh", "Qh", "Kh",
                 "Ac", "2c", "3c", "4c", "5c", "6c", "7c", "8c", "9c", "Tc", "Jc", "Qc", "Kc",
                 "Ad", "2d", "3d", "4d", "5d", "6d", "7d", "8d", "9d", "Td", "Jd", "Qd", "Kd",
                 "As", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "Ts", "Js", "Qs", "Ks"],
        "discard_pile": [],
        "upcard": None,
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
        "player_0_turn": True,
        "wall": False
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if action == "Draw stock":
        new_state["deck"].append(new_state["discard_pile"].pop())
        new_state["phase"] = "Draw"
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["deck"].pop(0)
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        new_state["player_0_hand"].remove(card_to_discard)
        new_state["discard_pile"].append(card_to_discard)
        new_state["phase"] = "Discard"
    elif action == "Knock":
        new_state["knock_card"] = 10
        new_state["phase"] = "Knock"
    elif action == "Done":
        new_state["phase"] = "Knock"
    elif action == "Pass":
        new_state["phase"] = "Knock"
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return 0 if state["player_0_turn"] else 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state["phase"] == "Wall":
        return [0.0, 0.0]
    else:
        return [state["player_0_deadwood"], state["player_1_deadwood"]]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["phase"] == "Wall":
        return []
    elif state["phase"] == "Knock":
        return ["Knock", "Done"]
    elif state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    else:
        return ["Draw stock", "Draw upcard"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        "upcard": state["upcard"],
        "discard_pile": state["discard_pile"],
        "deck": state["deck"],
        "knock_card": state["knock_card"],
        "player_0_hand": state["player_0_hand"],
        "player_1_hand": state["player_1_hand"],
        "player_0_deadwood": state["player_0_deadwood"],
        "player_1_deadwood": state["player_1_deadwood"],
        "player_0_melds": state["player_0_melds"],
        "player_1_melds": state["player_1_melds"],
        "player_0_meld_count": state["player_0_meld_count"],
        "player_1_meld_count": state["player_1_meld_count"],
        "player_0_turn": state["player_0_turn"],
        "wall": state["wall"]
    }
    player_1_obs = {
        "upcard": state["upcard"],
        "discard_pile": state["discard_pile"],
        "deck": state["deck"],
        "knock_card": state["knock_card"],
        "player_0_hand": state["player_1_hand"],
        "player_1_hand": state["player_0_hand"],
        "player_0_deadwood": state["player_1_deadwood"],
        "player_1_deadwood": state["player_0_deadwood"],
        "player_0_melds": state["player_1_melds"],
        "player_1_melds": state["player_0_melds"],
        "player_0_meld_count": state["player_1_meld_count"],
        "player_1_meld_count": state["player_0_meld_count"],
        "player_0_turn": not state["player_0_turn"],
        "wall": state["wall"]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ["Draw stock", "Action: Ah", "Knock"]
    else:
        return ["Draw stock", "Action: Ac", "Knock"]