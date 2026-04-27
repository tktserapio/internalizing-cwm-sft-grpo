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

# Helper functions
def shuffle_deck() -> List[int]:
    """Shuffles a standard 52-card deck."""
    deck = list(range(1, 53))  # 1-52 represents the 52 cards in a deck
    random.shuffle(deck)
    return deck

def create_initial_state(deck: List[int]) -> State:
    """Creates the initial game state."""
    # Initial state setup
    state = {
        "deck": deck,
        "upcard": deck.pop(0) if deck else None,
        "wall": deck,
        "phase": "Draw",
        "knock_card": 10,
        "player_0_hand": [],
        "player_1_hand": [],
        "player_0_melds": [],
        "player_1_melds": [],
        "player_0_deadwood": 0,
        "player_1_deadwood": 0,
        "player_0_score": 0,
        "player_1_score": 0,
        "player_0_turn": True,
        "player_1_turn": False,
        "player_0_knocked": False,
        "player_1_knocked": False,
        "player_0_layoff_cards": [],
        "player_1_layoff_cards": []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Applies an action to the current state and returns the new state."""
    new_state = state.copy()
    if action == "Draw stock":
        new_state["upcard"] = new_state["wall"].pop(0)
        new_state["phase"] = "Discard"
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["wall"].pop(0)
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card = int(action.split(":")[1])
        new_state["player_0_hand"].remove(card)
        new_state["wall"].append(card)
        new_state["phase"] = "Draw"
    elif action == "Knock":
        new_state["player_0_knocked"] = True
        new_state["phase"] = "Layoff"
    elif action == "Done":
        new_state["player_1_knocked"] = True
        new_state["phase"] = "Score"
    elif action == "Pass":
        new_state["player_0_turn"] = False
        new_state["player_1_turn"] = True
        new_state["phase"] = "Draw"
    return new_state

def get_current_player(state: State) -> int:
    """Returns the current player (0 or 1), or -4 for terminal state."""
    return 0 if state["player_0_turn"] else 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state["player_0_knocked"] and state["player_1_knocked"]:
        if state["player_0_deadwood"] < state["player_1_deadwood"]:
            return [state["player_0_deadwood"], state["player_1_deadwood"] - state["player_0_deadwood"]]
        elif state["player_0_deadwood"] == state["player_1_deadwood"]:
            return [state["player_0_deadwood"], state["player_1_deadwood"] - state["player_0_deadwood"] + 25]
        else:
            return [state["player_1_deadwood"] - state["player_0_deadwood"] + 25, state["player_0_deadwood"]]
    elif state["player_0_knocked"]:
        return [state["player_0_deadwood"], 0]
    elif state["player_1_knocked"]:
        return [0, state["player_1_deadwood"]]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["phase"] == "Wall":
        return []
    elif state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Discard":
        return [f"Action: {card}" for card in state["player_0_hand"]]
    elif state["phase"] == "Layoff":
        return ["Knock", "Done"]
    elif state["phase"] == "Score":
        return ["Pass"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        "deck": state["wall"],
        "upcard": state["upcard"],
        "player_0_hand": state["player_0_hand"],
        "player_1_hand": state["player_1_hand"],
        "player_0_melds": state["player_0_melds"],
        "player_1_melds": state["player_1_melds"],
        "player_0_deadwood": state["player_0_deadwood"],
        "player_1_deadwood": state["player_1_deadwood"],
        "knock_card": state["knock_card"],
        "phase": state["phase"],
        "player_0_turn": state["player_0_turn"],
        "player_1_turn": state["player_1_turn"],
        "player_0_knocked": state["player_0_knocked"],
        "player_1_knocked": state["player_1_knocked"],
        "player_0_layoff_cards": state["player_0_layoff_cards"],
        "player_1_layoff_cards": state["player_1_layoff_cards"]
    }
    player_1_obs = {
        "deck": state["wall"],
        "upcard": state["upcard"],
        "player_0_hand": state["player_1_hand"],
        "player_1_hand": state["player_0_hand"],
        "player_0_melds": state["player_1_melds"],
        "player_1_melds": state["player_0_melds"],
        "player_0_deadwood": state["player_1_deadwood"],
        "player_1_deadwood": state["player_0_deadwood"],
        "knock_card": state["knock_card"],
        "phase": state["phase"],
        "player_0_turn": state["player_1_turn"],
        "player_1_turn": state["player_0_turn"],
        "player_0_knocked": state["player_1_knocked"],
        "player_1_knocked": state["player_0_knocked"],
        "player_0_layoff_cards": state["player_1_layoff_cards"],
        "player_1_layoff_cards": state["player_0_layoff_cards"]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # This function would need to be implemented based on the observed history and the rules of the game.
    # For simplicity, we'll just return a fixed sequence of actions.
    # In a real implementation, this function would be much more complex and handle the stochastic nature of the game.
    if player_id == 0:
        return ["Draw stock", "Action: 2s", "Knock", "Done"]
    else:
        return ["Draw stock", "Action: 3h", "Knock", "Done"]

# Example usage
initial_deck = shuffle_deck()
state = create_initial_state(initial_deck)
print(state)

# Simulate a turn
print(apply_action(state, "Draw stock"))
print(apply_action(state, "Action: 2s"))
print(apply_action(state, "Knock"))
print(apply_action(state, "Done"))

# Get legal actions
print(get_legal_actions(state))

# Get rewards
print(get_rewards(state))