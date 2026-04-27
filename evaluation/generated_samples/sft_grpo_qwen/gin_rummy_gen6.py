import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def parse_card(card_str: str) -> Tuple[int, int]:  # (rank, suit)
    rank, suit = card_str[:-1], card_str[-1]
    return int(rank), suit

def get_initial_state() -> State:
    # Initial state setup
    state = {
        "deck": ["A♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠",
                 "A♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣",
                 "A♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦",
                 "A♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥"],
        "upcard": None,
        "dealer": 0,
        "knock_card": 10,
        "phase": "Draw",
        "player_0_hand": [],
        "player_1_hand": [],
        "player_0_melds": [],
        "player_1_melds": [],
        "player_0_deadwood": 0,
        "player_1_deadwood": 0,
        "wall": []
    }
    return state

def apply_action(state: State, action: Action) -> State:
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
        new_state["wall"].append(card)
        new_state["phase"] = "Knock"
    elif action == "Knock":
        new_state["knock_card"] = 10
        new_state["phase"] = "Layoff"
        new_state["player_0_melds"], new_state["player_1_melds"] = [], []
        new_state["player_0_deadwood"], new_state["player_1_deadwood"] = 0, 0
    elif action == "Done":
        new_state["phase"] = "Layoff"
    elif action == "Pass":
        new_state["phase"] = "Layoff"
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    return state["dealer"]

def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    if state["phase"] == "Wall":
        return [0.0, 0.0]
    elif state["phase"] == "Layoff":
        knocker_deadwood = state["player_0_deadwood"] if state["dealer"] == 0 else state["player_1_deadwood"]
        opponent_deadwood = state["player_1_deadwood"] if state["dealer"] == 0 else state["player_0_deadwood"]
        if knocker_deadwood < opponent_deadwood:
            return [knocker_deadwood, opponent_deadwood - knocker_deadwood]
        elif knocker_deadwood == opponent_deadwood:
            return [knocker_deadwood, opponent_deadwood - knocker_deadwood + 25]
        else:
            return [opponent_deadwood, 0.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Discard":
        return ["Action: " + card for card in state["player_0_hand"]]
    elif state["phase"] == "Knock":
        return ["Knock", "Done"]
    elif state["phase"] == "Layoff":
        return ["Pass"]
    else:
        return []

def get_observations(state: State) -> List[PlayerObservation]:
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
        "wall": state["wall"]
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
        "wall": state["wall"]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    history = obs_action_history[player_id]
    if len(history) > 0 and history[-1][1] is None:
        history.pop()
    while True:
        action = history[-1][1]
        if action is None:
            break
        yield action
        history.pop()