import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Tuple, Dict, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def shuffle_deck() -> List[int]:
    """Shuffles the deck and returns the shuffled deck as a list of integers."""
    deck = list(range(1, 53))
    random.shuffle(deck)
    return deck

def create_initial_state(deck: List[int]) -> State:
    """Creates the initial state of the game."""
    # Initial state variables
    current_player = 0
    upcard = deck.pop(0) if deck else None
    discard_pile = []
    deadwood = {0: [], 1: []}
    melds = {0: [], 1: []}
    knock_card = 10  # Default knock card value
    phase = "Draw"
    obs_action_history = []

    return {
        "current_player": current_player,
        "upcard": upcard,
        "discard_pile": discard_pile,
        "deadwood": deadwood,
        "melds": melds,
        "knock_card": knock_card,
        "phase": phase,
        "obs_action_history": obs_action_history,
    }

def apply_action(state: State, action: Action) -> State:
    """Applies the given action to the current state and returns the new state."""
    new_state = state.copy()
    current_player = get_current_player(new_state)
    player_id = current_player
    player_obs = new_state["player_0_obs"] if current_player == 0 else new_state["player_1_obs"]
    
    if action == "Draw stock":
        new_state["upcard"] = deck.pop(0) if deck else None
        new_state["discard_pile"].append(player_obs["upcard"])
        new_state["player_0_obs"]["upcard"] = new_state["upcard"]
        new_state["player_1_obs"]["upcard"] = new_state["upcard"]
        new_state["phase"] = "Knock"
    elif action == "Draw upcard":
        new_state["upcard"] = player_obs["discard_pile"].pop()
        new_state["discard_pile"].append(new_state["upcard"])
        new_state["player_0_obs"]["upcard"] = new_state["upcard"]
        new_state["player_1_obs"]["upcard"] = new_state["upcard"]
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card_to_discard = int(action.split(":")[1])
        new_state["discard_pile"].append(card_to_discard)
        new_state["player_0_obs"]["discard_pile"].append(card_to_discard)
        new_state["player_1_obs"]["discard_pile"].append(card_to_discard)
        new_state["deadwood"][current_player].append(card_to_discard)
        new_state["phase"] = "Knock"
    elif action == "Action: Knock":
        new_state["knock_card"] = knock_card
        new_state["phase"] = "Layoff"
        new_state["obs_action_history"].append((player_obs, action))
    elif action == "Action: Done":
        new_state["phase"] = "Done"
    elif action == "Pass":
        new_state["phase"] = "Done"
    else:
        raise ValueError(f"Invalid action: {action}")
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns the current player ID."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. For simplicity, returns [0.0, 0.0] until meaningful reward information is available."""
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for the current state. Empty list if the state is terminal."""
    current_player = get_current_player(state)
    if state["phase"] == "Wall":
        return []
    elif state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Discard":
        return ["Action: " + str(card) for card in state["deadwood"][current_player]] + ["Action: Knock", "Pass"]
    else:  # Knock phase
        return ["Action: Done"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns the observations for each player."""
    current_player = get_current_player(state)
    return [
        {
            "upcard": state["upcard"],
            "discard_pile": state["discard_pile"],
            "deadwood": state["deadwood"][current_player],
            "melds": state["melds"][current_player],
            "knock_card": state["knock_card"],
            "phase": state["phase"],
            "obs_action_history": state["obs_action_history"],
        },
        {
            "upcard": state["upcard"],
            "discard_pile": state["discard_pile"],
            "deadwood": state["deadwood"][1 - current_player],
            "melds": state["melds"][1 - current_player],
            "knock_card": state["knock_card"],
            "phase": state["phase"],
            "obs_action_history": state["obs_action_history"],
        }
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Implementing this function would require a more complex logic to handle all possible scenarios.
    # For simplicity, we'll just return a fixed sequence of actions that explain the current state.
    # This is a placeholder and should be replaced with actual stochastic sampling logic.
    return [
        "Draw stock",
        "Action: 2s",
        "Action: 3s",
        "Action: 4s",
        "Action: 5s",
        "Action: 6s",
        "Action: 7s",
        "Action: 8s",
        "Action: 9s",
        "Action: Ts",
        "Action: Js",
        "Action: Qs",
        "Action: As",
        "Action: 2c",
        "Action: 3c",
        "Action: 4c",
        "Action: 5c",
        "Action: 6c",
        "Action: 7c",
        "Action: 8c",
        "Action: 9c",
        "Action: Tc",
        "Action: Jc",
        "Action: Qc",
        "Action: Ac",
        "Action: 2d",
        "Action: 3d",
        "Action: 4d",
        "Action: 5d",
        "Action: 6d",
        "Action: 7d",
        "Action: 8d",
        "Action: 9d",
        "Action: Td",
        "Action: Jd",
        "Action: Qd",
        "Action: Ad",
        "Action: 2h",
        "Action: 3h",
        "Action: 4h",
        "Action: 5h",
        "Action: 6h",
        "Action: 7h",
        "Action: 8h",
        "Action: 9h",
        "Action: Th",
        "Action: Jh",
        "Action: Qh",
        "Action: Ah",
        "Action: Done"
    ]