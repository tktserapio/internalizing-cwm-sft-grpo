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
def parse_state(state: State) -> State:
    """Helper function to parse the state dictionary into a more readable format."""
    return {
        "upcard": state.get("upcard"),
        "dealer": state.get("dealer"),
        "deck": state.get("deck"),
        "wall": state.get("wall"),
        "knock_card": state.get("knock_card"),
        "player_0_hand": state.get("player_0_hand"),
        "player_1_hand": state.get("player_1_hand"),
        "player_0_deadwood": state.get("player_0_deadwood"),
        "player_1_deadwood": state.get("player_1_deadwood"),
        "phase": state.get("phase")
    }

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial state setup
    upcard = random.choice(list(range(1, 14))) * 13 + random.choice([1, 10])  # Random upcard
    dealer = random.choice([0, 1])  # Random dealer
    deck = list(range(1, 14)) * 4  # Full deck
    wall = []  # Wall is empty initially
    knock_card = 10  # Default knock card value
    player_0_hand = random.sample(deck, 7)  # Player 0's hand
    player_1_hand = [card for card in deck if card not in player_0_hand]  # Player 1's hand
    player_0_deadwood = sum(card // 13 for card in player_0_hand)  # Calculate deadwood
    player_1_deadwood = sum(card // 13 for card in player_1_hand)  # Calculate deadwood
    phase = "Draw"  # Initial phase is Draw
    return {
        "upcard": upcard,
        "dealer": dealer,
        "deck": deck,
        "wall": wall,
        "knock_card": knock_card,
        "player_0_hand": player_0_hand,
        "player_1_hand": player_1_hand,
        "player_0_deadwood": player_0_deadwood,
        "player_1_deadwood": player_1_deadwood,
        "phase": phase
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if action == "Draw stock":
        new_state["deck"].append(new_state["wall"].pop(0))
    elif action == "Draw upcard":
        new_state["deck"].append(new_state["wall"].pop(0))
    elif action.startswith("Action: "):
        card_to_discard = int(action.split(":")[1])
        new_state["deck"].append(card_to_discard)
        new_state["wall"].append(card_to_discard)
        new_state["player_0_hand"].remove(card_to_discard)
        new_state["player_1_hand"].remove(card_to_discard)
        new_state["player_0_deadwood"] -= card_to_discard // 13
        new_state["player_1_deadwood"] -= card_to_discard // 13
    elif action == "Knock":
        new_state["phase"] = "Knock"
        new_state["knock_card"] = 10  # Default knock card value
        new_state["knock"] = True
    elif action == "Done":
        new_state["phase"] = "Knock"
        new_state["knock"] = False
    elif action == "Pass":
        new_state["phase"] = "Wall"
        new_state["wall"] = new_state["deck"]
        new_state["deck"] = []
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["phase"] == "Wall":
        return -4
    return state["dealer"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["phase"] == "Wall":
        return [0.0, 0.0]
    return [state["player_0_deadwood"], state["player_1_deadwood"]]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["phase"] == "Wall":
        return []
    if state["phase"] == "Knock":
        return ["Action: Done"]
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        "upcard": state["upcard"],
        "dealer": state["dealer"],
        "deck": state["deck"],
        "wall": state["wall"],
        "knock_card": state["knock_card"],
        "player_0_hand": state["player_0_hand"],
        "player_1_hand": state["player_1_hand"],
        "player_0_deadwood": state["player_0_deadwood"],
        "player_1_deadwood": state["player_1_deadwood"],
        "phase": state["phase"]
    }
    player_1_obs = {
        "upcard": state["upcard"],
        "dealer": state["dealer"],
        "deck": state["deck"],
        "wall": state["wall"],
        "knock_card": state["knock_card"],
        "player_0_hand": state["player_1_hand"],
        "player_1_hand": state["player_0_hand"],
        "player_0_deadwood": state["player_1_deadwood"],
        "player_1_deadwood": state["player_0_deadwood"],
        "phase": state["phase"]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ["Draw stock", "Action: 2c", "Knock"]
    else:
        return ["Draw stock", "Action: 3d", "Knock"]