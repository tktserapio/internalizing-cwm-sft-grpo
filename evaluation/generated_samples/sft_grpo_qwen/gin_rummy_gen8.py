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

# Helper function to create a new state
def create_new_state(current_state: State) -> State:
    return {
        "phase": current_state["phase"],
        "deck": current_state["deck"],
        "upcard": current_state["upcard"],
        "dealer": current_state["dealer"],
        "players": current_state["players"],
        "knock_card": current_state["knock_card"],
        "round_number": current_state["round_number"]
    }

# Required Functions
def get_initial_state() -> State:
    # Initial state setup
    deck = [str(card) for card in range(1, 53)]
    random.shuffle(deck)
    players = [{"hand": [], "melds": [], "deadwood": []}, {"hand": [], "melds": [], "deadwood": []}]
    current_player = 0
    upcard = deck.pop()
    dealer = 0
    knock_card = 10
    round_number = 1
    return {
        "phase": "Draw",
        "deck": deck,
        "upcard": upcard,
        "dealer": dealer,
        "players": players,
        "knock_card": knock_card,
        "round_number": round_number
    }

def apply_action(state: State, action: Action) -> State:
    new_state = create_new_state(state)
    if action == "Draw stock":
        new_state["deck"].append(new_state["upcard"])
        new_state["upcard"] = new_state["deck"].pop()
        new_state["phase"] = "Discard"
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["deck"].pop()
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        new_state["players"][state["current_player"]]["hand"].remove(card_to_discard)
        new_state["players"][state["current_player"]]["deadwood"].append(card_to_discard)
        new_state["deck"].append(card_to_discard)
        new_state["upcard"] = new_state["deck"].pop()
        new_state["phase"] = "Discard"
    elif action == "Action: Knock":
        new_state["phase"] = "Knock"
        new_state["knock_card"] = int(action.split(": ")[1])
        new_state["players"][state["current_player"]]["deadwood"] = []
        new_state["players"][state["current_player"]]["melds"] = []
    elif action == "Action: Done":
        new_state["phase"] = "Knock"
    elif action == "Pass":
        new_state["phase"] = "Knock"
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    if state["phase"] == "Wall":
        return [0.0, 0.0]
    elif state["phase"] == "Knock":
        knocker_deadwood = sum([int(card[:-1]) for card in state["players"][0]["deadwood"]])
        opponent_deadwood = sum([int(card[:-1]) for card in state["players"][1]["deadwood"]])
        if knocker_deadwood <= state["knock_card"]:
            return [knocker_deadwood, opponent_deadwood]
        else:
            return [opponent_deadwood, knocker_deadwood]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    if state["phase"] == "Wall":
        return []
    elif state["phase"] == "Knock":
        return ["Action: Done"]
    elif state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    else:
        return ["Action: <card>", "Action: Knock", "Action: Done", "Pass"]

def get_observations(state: State) -> List[PlayerObservation]:
    player_0_obs = {
        "phase": state["phase"],
        "deck": state["deck"],
        "upcard": state["upcard"],
        "dealer": state["dealer"],
        "players": state["players"][0],
        "knock_card": state["knock_card"],
        "round_number": state["round_number"]
    }
    player_1_obs = {
        "phase": state["phase"],
        "deck": state["deck"],
        "upcard": state["upcard"],
        "dealer": state["dealer"],
        "players": state["players"][1],
        "knock_card": state["knock_card"],
        "round_number": state["round_number"]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    if player_id == 0:
        player = obs_action_history[-1][0]["players"]
    else:
        player = obs_action_history[-1][0]["players"]
    if player_id == 0:
        player_0_obs = obs_action_history[-1][0]
        player_1_obs = obs_action_history[-2][0]
    else:
        player_0_obs = obs_action_history[-2][0]
        player_1_obs = obs_action_history[-1][0]
    if player_0_obs["phase"] == "Knock":
        return ["Action: " + player_id + ": " + player[player_id]["deadwood"][0]]
    else:
        return ["Draw stock", "Draw upcard", "Action: " + player_id + ": " + player[player_id]["deadwood"][0], "Action: Knock"]