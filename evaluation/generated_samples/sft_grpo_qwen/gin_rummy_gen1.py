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

# Helper functions
def parse_card(card_str: str) -> tuple[int, int]:
    """Parses a card string into a tuple (suit, rank)"""
    suit, rank = card_str[:-1], int(card_str[-1])
    return suit, rank

def is_valid_meld(meld: List[str]) -> bool:
    """Checks if a meld is valid (set or run)"""
    if len(meld) == 3 or len(meld) == 4:
        ranks = [int(c[-1]) for c in meld]
        suits = [c[0] for c in meld]
        return len(set(ranks)) == 1 or (len(set(suits)) == 1 and max(ranks) - min(ranks) == len(meld) - 1)
    return False

def is_valid_deadwood(deadwood: List[str]) -> bool:
    """Checks if the deadwood is valid (no invalid melds)"""
    return all(not is_valid_meld(meld) for meld in deadwood)

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial state setup
    state = {
        "deck": ["Ah", "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th", "Jh", "Qh", "Kh",
                 "Ac", "2c", "3c", "4c", "5c", "6c", "7c", "8c", "9c", "Tc", "Jc", "Qc", "Kc",
                 "Ad", "2d", "3d", "4d", "5d", "6d", "7d", "8d", "9d", "Td", "Jd", "Qd", "Kd",
                 "As", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "Ts", "Js", "Qs", "Ks"],
        "upcard": None,
        "dealer": 0,
        "knock_card": 10,
        "phase": "Draw",
        "player_0_hand": [],
        "player_1_hand": [],
        "player_0_melds": [],
        "player_1_melds": [],
        "player_0_deadwood": [],
        "player_1_deadwood": [],
        "player_0_score": 0,
        "player_1_score": 0
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if action == "Draw stock":
        new_state["upcard"] = new_state["deck"].pop(0)
        new_state["phase"] = "Discard"
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["deck"].pop(0)
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card = action.split(": ")[1]
        new_state["player_0_hand"].remove(card)
        new_state["player_1_hand"].remove(card)
        new_state["player_0_melds"] = [m for m in new_state["player_0_melds"] if card not in m]
        new_state["player_1_melds"] = [m for m in new_state["player_1_melds"] if card not in m]
        new_state["player_0_deadwood"].append(card)
        new_state["player_1_deadwood"].append(card)
        new_state["phase"] = "Knock"
    elif action == "Action: Knock":
        new_state["knock_card"] = 10
        new_state["phase"] = "Layoff"
    elif action == "Action: Done":
        new_state["phase"] = "Done"
    elif action == "Pass":
        new_state["phase"] = "Wall"
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["phase"] == "Knock":
        return -4
    return state["dealer"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["phase"] == "Knock":
        return [state["player_0_score"], state["player_1_score"]]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["phase"] == "Wall":
        return []
    if state["phase"] == "Knock":
        return ["Action: Done"]
    if state["phase"] == "Done":
        return []
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    if state["phase"] == "Discard":
        return [f"Action: {card}" for card in state["player_0_hand"] + state["player_1_hand"]]
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        "phase": state["phase"],
        "upcard": state["upcard"],
        "dealer": state["dealer"],
        "knock_card": state["knock_card"],
        "player_0_hand": state["player_0_hand"],
        "player_1_hand": state["player_1_hand"],
        "player_0_melds": state["player_0_melds"],
        "player_1_melds": state["player_1_melds"],
        "player_0_deadwood": state["player_0_deadwood"],
        "player_1_deadwood": state["player_1_deadwood"],
        "player_0_score": state["player_0_score"],
        "player_1_score": state["player_1_score"]
    }
    player_1_obs = {
        "phase": state["phase"],
        "upcard": state["upcard"],
        "dealer": state["dealer"],
        "knock_card": state["knock_card"],
        "player_0_hand": state["player_1_hand"],
        "player_1_hand": state["player_0_hand"],
        "player_0_melds": state["player_1_melds"],
        "player_1_melds": state["player_0_melds"],
        "player_0_deadwood": state["player_1_deadwood"],
        "player_1_deadwood": state["player_0_deadwood"],
        "player_0_score": state["player_1_score"],
        "player_1_score": state["player_0_score"]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we'll just randomly select actions from the legal ones
    legal_actions = get_legal_actions(resample_history.get_initial_state())
    return [random.choice(legal_actions) for _ in obs_action_history]