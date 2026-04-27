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

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial state setup
    deck = list(range(1, 53))  # 52 cards + 1 wild card
    random.shuffle(deck)
    stockpile = deck[:5]
    discard_pile = []
    hands = {0: [], 1: []}
    current_player = 0
    phase = "Draw"
    deadwood = {0: 0, 1: 0}
    knock_card = 10  # Default knock card value
    observations = [{}, {}]
    
    return {
        "deck": deck,
        "stockpile": stockpile,
        "discard_pile": discard_pile,
        "hands": hands,
        "current_player": current_player,
        "phase": phase,
        "deadwood": deadwood,
        "knock_card": knock_card,
        "observations": observations
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    player_id = get_current_player(new_state)
    player_hand = new_state["hands"][player_id]
    
    if action == "Draw stock":
        new_state["stockpile"].append(player_hand.pop())
        new_state["discard_pile"].append(player_hand.pop())
        new_state["hands"][player_id] = player_hand
        new_state["phase"] = "Draw"
        new_state["deadwood"][player_id] = sum(card // 13 for card in player_hand)
        return new_state
    
    elif action == "Draw upcard":
        new_state["stockpile"].append(player_hand.pop())
        new_state["discard_pile"].append(player_hand.pop())
        new_state["hands"][player_id] = player_hand
        new_state["phase"] = "Discard"
        new_state["deadwood"][player_id] = sum(card // 13 for card in player_hand)
        return new_state
    
    elif action.startswith("Action: "):
        card_to_discard = int(action.split(":")[1])
        new_state["hands"][player_id].remove(card_to_discard)
        new_state["discard_pile"].append(card_to_discard)
        new_state["phase"] = "Discard"
        new_state["deadwood"][player_id] = sum(card // 13 for card in player_hand)
        return new_state
    
    elif action == "Knock":
        new_state["phase"] = "Knock"
        new_state["knock_card"] = 10  # Default knock card value
        return new_state
    
    elif action == "Done":
        new_state["phase"] = "Knock"
        return new_state
    
    elif action == "Pass":
        new_state["phase"] = "Knock"
        return new_state
    
    else:
        raise ValueError(f"Invalid action: {action}")

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["phase"] == "Knock":
        return [0.0, 0.0]
    else:
        return [state["deadwood"][0], state["deadwood"][1]]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    player_id = get_current_player(state)
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Discard":
        return ["Action: " + str(card) for card in state["hands"][player_id]] + ["Knock", "Done", "Pass"]
    else:
        return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = state["hands"][0]
    player_1_obs = state["hands"][1]
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    return ["Draw stock", "Action: 2h", "Knock", "Done"]