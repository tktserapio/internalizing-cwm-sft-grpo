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

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initialize the deck and shuffle it
    deck = list(range(1, 53))  # 1-52 for cards, 53 is the upcard
    random.shuffle(deck)
    upcard = deck.pop()
    stockpile = deck.copy()
    
    # Initial state setup
    state = {
        "deck": deck,
        "stockpile": stockpile,
        "upcard": upcard,
        "phase": "Draw",
        "player_0_hand": [],
        "player_1_hand": [],
        "player_0_deadwood": 0,
        "player_1_deadwood": 0,
        "player_0_melds": [],
        "player_1_melds": [],
        "player_0_knocked": False,
        "player_1_knocked": False,
        "player_0_turn": True,
        "player_1_turn": False,
        "knock_card": 10,
        "round_over": False
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == "Draw stock":
        new_state["stockpile"].append(new_state["upcard"])
        new_state["upcard"] = new_state["stockpile"].pop()
        new_state["phase"] = "Discard"
        new_state["player_0_turn"], new_state["player_1_turn"] = new_state["player_1_turn"], new_state["player_0_turn"]
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["stockpile"].pop()
        new_state["phase"] = "Discard"
        new_state["player_0_turn"], new_state["player_1_turn"] = new_state["player_1_turn"], new_state["player_0_turn"]
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        new_state["player_0_hand"].remove(card_to_discard)
        new_state["stockpile"].append(card_to_discard)
        new_state["phase"] = "Discard"
        new_state["player_0_turn"], new_state["player_1_turn"] = new_state["player_1_turn"], new_state["player_0_turn"]
    elif action == "Knock":
        new_state["player_0_knocked"] = True
        new_state["player_1_knocked"] = True
        new_state["phase"] = "Layoff"
    elif action == "Done":
        new_state["player_0_knocked"] = True
        new_state["player_1_knocked"] = True
        new_state["phase"] = "Layoff"
    elif action == "Pass":
        new_state["player_0_turn"], new_state["player_1_turn"] = new_state["player_1_turn"], new_state["player_0_turn"]
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return 0 if state["player_0_turn"] else 1

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards for the current state
def get_rewards(state: State) -> List[float]:
    if state["round_over"]:
        player_0_reward = 0.0
        player_1_reward = 0.0
        if state["player_0_knocked"] and state["player_1_knocked"]:
            player_0_reward = state["player_1_deadwood"]
            player_1_reward = state["player_0_deadwood"]
        elif state["player_0_knocked"] and not state["player_1_knocked"]:
            player_0_reward = state["player_1_deadwood"] + 25
            player_1_reward = 0.0
        elif not state["player_0_knocked"] and state["player_1_knocked"]:
            player_0_reward = 0.0
            player_1_reward = state["player_0_deadwood"] + 25
        elif state["player_0_deadwood"] == 0:
            player_0_reward = state["player_1_deadwood"] + 25
            player_1_reward = 0.0
        elif state["player_1_deadwood"] == 0:
            player_0_reward = 0.0
            player_1_reward = state["player_0_deadwood"] + 25
        return [player_0_reward, player_1_reward]
    return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    player_id = get_current_player(state)
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Discard":
        if player_id == 0:
            return ["Action: " + card for card in state["player_0_hand"]]
        else:
            return ["Action: " + card for card in state["player_1_hand"]]
    elif state["phase"] == "Layoff":
        return ["Knock", "Done"]
    else:
        return []

# Get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    player_0_obs = {
        "phase": state["phase"],
        "deck": state["deck"],
        "stockpile": state["stockpile"],
        "upcard": state["upcard"],
        "player_0_hand": state["player_0_hand"],
        "player_0_deadwood": state["player_0_deadwood"],
        "player_0_melds": state["player_0_melds"],
        "player_1_hand": state["player_1_hand"],
        "player_1_deadwood": state["player_1_deadwood"],
        "player_1_melds": state["player_1_melds"],
        "player_0_knocked": state["player_0_knocked"],
        "player_1_knocked": state["player_1_knocked"],
        "knock_card": state["knock_card"],
        "round_over": state["round_over"]
    }
    player_1_obs = {
        "phase": state["phase"],
        "deck": state["deck"],
        "stockpile": state["stockpile"],
        "upcard": state["upcard"],
        "player_0_hand": state["player_1_hand"],
        "player_0_deadwood": state["player_1_deadwood"],
        "player_0_melds": state["player_1_melds"],
        "player_1_hand": state["player_0_hand"],
        "player_1_deadwood": state["player_0_deadwood"],
        "player_0_knocked": state["player_1_knocked"],
        "player_1_knocked": state["player_0_knocked"],
        "knock_card": state["knock_card"],
        "round_over": state["round_over"]
    }
    return [player_0_obs, player_1_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Placeholder for resampling logic
    # For simplicity, we'll just return a random valid action
    legal_actions = get_legal_actions(resample_history.observation)
    return [random.choice(legal_actions)]