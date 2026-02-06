from typing import Any, Dict, List, Optional, Tuple
import random

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
P0, P1, CHANCE, TERMINAL = 0, 1, -1, -4
WIN_SCORE = 100
DIE_SIDES = 6

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "scores": [0, 0],          # Permanent scores for each player
        "turn_total": 0,           # Points accumulated this turn
        "current_player": P0,
        "waiting_for_chance": False,  # True if we need a die roll
        "is_terminal": False,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = {
        "scores": state["scores"].copy(),
        "turn_total": state["turn_total"],
        "current_player": state["current_player"],
        "waiting_for_chance": state["waiting_for_chance"],
        "is_terminal": state["is_terminal"],
        "winner": state["winner"]
    }

    if state["current_player"] == CHANCE:
        # Die roll outcome
        die_value = int(action)
        current = state["waiting_for_chance"]  # Player who rolled

        if die_value == 1:
            # Pigged out - lose turn total, switch players
            new_state["turn_total"] = 0
            new_state["current_player"] = 1 - current
            new_state["waiting_for_chance"] = False
        else:
            # Add to turn total, continue turn
            new_state["turn_total"] = state["turn_total"] + die_value
            new_state["current_player"] = current
            new_state["waiting_for_chance"] = False

    elif action == "roll":
        # Player chooses to roll
        new_state["waiting_for_chance"] = state["current_player"]
        new_state["current_player"] = CHANCE

    elif action == "hold":
        # Player banks points
        current = state["current_player"]
        new_score = state["scores"][current] + state["turn_total"]
        new_state["scores"][current] = new_score
        new_state["turn_total"] = 0

        if new_score >= WIN_SCORE:
            new_state["is_terminal"] = True
            new_state["winner"] = current
            new_state["current_player"] = TERMINAL
        else:
            new_state["current_player"] = 1 - current

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player, with -1 for chance and -4 for terminal."""
    if state["is_terminal"]:
        return TERMINAL
    if state["current_player"] == CHANCE:
        return CHANCE
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    names = {P0: "Player 0", P1: "Player 1", CHANCE: "Chance", TERMINAL: "Terminal"}
    return names.get(player_id, "Unknown")

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. Non-zero only at terminal states."""
    if not state["is_terminal"]:
        return [0.0, 0.0]

    if state["winner"] == P0:
        return [1.0, -1.0]
    else:
        return [-1.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["is_terminal"]:
        return []

    if state["current_player"] == CHANCE:
        return [str(i) for i in range(1, DIE_SIDES + 1)]

    # Player actions
    actions = ["roll"]

    # Can only hold if we have points to bank
    if state["turn_total"] > 0:
        actions.append("hold")

    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. Pig is perfect information."""
    obs = {
        "scores": state["scores"],
        "turn_total": state["turn_total"],
        "current_player": state["current_player"]
    }
    return [obs, obs]
