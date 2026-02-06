from typing import Any, Dict, List, Optional, Tuple
import random

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
P0, P1, TERMINAL = 0, 1, -4
ACTIONS = ["C", "D"]  # Cooperate, Defect

# Payoff matrix: PAYOFFS[p0_action][p1_action] = (p0_reward, p1_reward)
PAYOFFS = {
    "C": {"C": (3.0, 3.0), "D": (0.0, 5.0)},
    "D": {"C": (5.0, 0.0), "D": (1.0, 1.0)}
}

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "p0_choice": None,
        "p1_choice": None,
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
    if player_id == P0: return "Player 0"
    if player_id == P1: return "Player 1"
    return "Terminal"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. Non-zero only at terminal states."""
    if not state["is_terminal"]:
        return [0.0, 0.0]

    p0_choice = state["p0_choice"]
    p1_choice = state["p1_choice"]
    p0_reward, p1_reward = PAYOFFS[p0_choice][p1_choice]
    # Normalize to zero-sum by subtracting mean
    mean_reward = (p0_reward + p1_reward) / 2
    return [p0_reward - mean_reward, p1_reward - mean_reward]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["is_terminal"]:
        return []
    return ACTIONS.copy()

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. Players only see their own choice until terminal."""
    if state["is_terminal"]:
        return [
            {"my_choice": state["p0_choice"], "opponent_choice": state["p1_choice"]},
            {"my_choice": state["p1_choice"], "opponent_choice": state["p0_choice"]}
        ]

    return [
        {"my_choice": state["p0_choice"]},
        {"my_choice": state["p1_choice"]}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    """Stochastically sample a history consistent with player_id's view."""
    if not obs_action_history:
        return []

    last_obs, last_action = obs_action_history[-1]
    my_choice = last_obs.get("my_choice")

    # Sample opponent's choice uniformly
    opponent_choice = random.choice(ACTIONS)

    if player_id == P0:
        history = []
        if my_choice is not None:
            history.append(my_choice)
        if "opponent_choice" in last_obs:
            history.append(last_obs["opponent_choice"])
        elif my_choice is not None:
            history.append(opponent_choice)
    else:
        history = []
        if "opponent_choice" in last_obs:
            history.append(last_obs["opponent_choice"])
        else:
            history.append(opponent_choice)
        if my_choice is not None:
            history.append(my_choice)

    if last_action is not None and (not history or history[-1] != last_action):
        history.append(last_action)

    return history
