from typing import Any, Dict, List, Optional, Tuple
import random

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
P0, P1, TERMINAL = 0, 1, -4
ACTIONS = ["H", "T"]  # Heads, Tails

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "p0_choice": None,  # P0's secret choice
        "p1_choice": None,  # P1's secret choice
        "current_player": P0,
        "is_terminal": False
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()

    if state["current_player"] == P0:
        new_state["p0_choice"] = action
        new_state["current_player"] = P1
    elif state["current_player"] == P1:
        new_state["p1_choice"] = action
        new_state["current_player"] = TERMINAL
        new_state["is_terminal"] = True

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player, or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    if player_id == P0: return "Player 0 (Matcher)"
    if player_id == P1: return "Player 1 (Mismatcher)"
    return "Terminal"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    p0_choice = state["p0_choice"]
    p1_choice = state["p1_choice"]

    if p0_choice is None or p1_choice is None:
        return [0.0, 0.0]

    # P0 wins if choices match, P1 wins if they differ
    if p0_choice == p1_choice:
        return [1.0, -1.0]  # Match: P0 wins
    else:
        return [-1.0, 1.0]  # Mismatch: P1 wins

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["is_terminal"]:
        return []
    return ACTIONS.copy()

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. Players only see their own choice until terminal."""
    if state["is_terminal"]:
        # At terminal, both see the full outcome
        return [
            {"my_choice": state["p0_choice"], "opponent_choice": state["p1_choice"]},
            {"my_choice": state["p1_choice"], "opponent_choice": state["p0_choice"]}
        ]

    # During play, players only see their own committed choice (if any)
    return [
        {"my_choice": state["p0_choice"]},
        {"my_choice": state["p1_choice"]}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    """Stochastically sample a history consistent with player_id's view.

    The player's own actions are known from obs_action_history.
    The opponent's action is sampled uniformly (hidden information).
    Returns full action sequence [P0_action, P1_action] from initial state.
    """
    if not obs_action_history:
        return []

    # The player's action is the recorded action from history
    player_action = obs_action_history[0][1]
    last_obs = obs_action_history[-1][0]

    # If terminal observation reveals opponent, use it; otherwise sample
    if "opponent_choice" in last_obs:
        opponent_action = last_obs["opponent_choice"]
    else:
        opponent_action = random.choice(ACTIONS)

    # Game order: P0 acts first, then P1
    if player_id == P0:
        return [player_action, opponent_action]
    else:
        return [opponent_action, player_action]
