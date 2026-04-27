import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper functions
def get_random_location():
    """Generates a random location within the 4x4 grid."""
    return random.randint(0, 3), random.randint(0, 3)

def get_quadrant(row, col):
    """Determines the quadrant based on the row and column coordinates."""
    if row < 2 and col < 2:
        return "Q1"
    elif row < 2 and col >= 2:
        return "Q2"
    elif row >= 2 and col < 2:
        return "Q3"
    else:
        return "Q4"

def get_initial_state():
    """Returns the initial game state before any actions are taken."""
    # Place player 0 in Q1 and player 1 in Q4
    p0_loc = get_random_location()
    p1_loc = (3, 3) if p0_loc == (0, 0) else (0, 3)
    return {
        "p0_loc": p0_loc,
        "p1_loc": p1_loc,
        "current_player": 0,
        "turn_count": 0,
        "quadrant_p0": get_quadrant(p0_loc[0], p0_loc[1]),
        "quadrant_p1": get_quadrant(p1_loc[0], p1_loc[1])
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if action == "place_p0:<row>,<col>":
        new_state["p0_loc"] = eval(action.split(":")[1])
        new_state["quadrant_p0"] = get_quadrant(new_state["p0_loc"][0], new_state["p0_loc"][1])
    elif action == "place_p1:<row>,<col>":
        new_state["p1_loc"] = eval(action.split(":")[1])
        new_state["quadrant_p1"] = get_quadrant(new_state["p1_loc"][0], new_state["p1_loc"][1])
    else:
        # Movement action
        row, col = new_state["p0_loc"]
        if action == "Up":
            new_state["p0_loc"] = (max(0, row - 1), col)
        elif action == "Down":
            new_state["p0_loc"] = (min(3, row + 1), col)
        elif action == "Left":
            new_state["p0_loc"] = (row, max(0, col - 1))
        elif action == "Right":
            new_state["p0_loc"] = (row, min(3, col + 1))
        elif action == "Stay":
            pass
        else:
            raise ValueError(f"Invalid action: {action}")
        new_state["quadrant_p0"] = get_quadrant(new_state["p0_loc"][0], new_state["p0_loc"][1])

    new_state["turn_count"] += 1
    new_state["current_player"] = 1 if new_state["current_player"] == 0 else 0
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["turn_count"] >= 20:
        return [0.0, 0.0]
    elif state["p0_loc"] == state["p1_loc"]:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    if state["current_player"] == 0:
        legal_actions.append("place_p0:<row>,<col>")
        legal_actions.append("place_p1:<row>,<col>")
        legal_actions.extend(["Up", "Down", "Left", "Right", "Stay"])
    else:
        legal_actions.extend(["place_p0:<row>,<col>", "place_p1:<row>,<col>"])
        legal_actions.append("Up")
        legal_actions.append("Down")
        legal_actions.append("Left")
        legal_actions.append("Right")
        legal_actions.append("Stay")
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_obs = {
        "My Loc": f"{state['p0_loc'][0]}, {state['p0_loc'][1]}",
        "Opponent Quadrant": state["quadrant_p1"]
    }
    p1_obs = {
        "My Loc": f"{state['p1_loc'][0]}, {state['p1_loc'][1]}",
        "Opponent Quadrant": state["quadrant_p0"]
    }
    return [p0_obs, p1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # This function would need to be implemented to generate a plausible history given the current observations.
    # For simplicity, we'll just return a fixed sequence of actions that lead to the current state.
    # In a real implementation, this would involve sampling from the possible histories that match the observations.
    # Here, we're returning a fixed sequence of actions that could have led to the current state.
    if player_id == 0:
        return ["place_p0:0,0", "Up", "Down", "Right", "Right", "Up", "Left", "Up"]
    else:
        return ["place_p1:3,3", "Down", "Down", "Left", "Left", "Up", "Right", "Up"]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    
    # Simulate a few turns
    for _ in range(8):
        print(f"\nTurn {_+1}:")
        print("Current State:", initial_state)
        current_player = get_current_player(initial_state)
        print(f"Current Player: {get_player_name(current_player)}")
        
        legal_actions = get_legal_actions(initial_state)
        print("Legal Actions:", legal_actions)
        
        # Randomly select an action
        action = random.choice(legal_actions)
        print(f"Selected Action: {action}")
        
        new_state = apply_action(initial_state, action)
        print("New State:", new_state)
        
        # Get observations
        observations = get_observations(new_state)
        print("Observations:", observations)
        
        # Get rewards
        rewards = get_rewards(new_state)
        print("Rewards:", rewards)
        
        # Resample history
        resampled_actions = resample_history([(obs, None) for obs in observations], current_player)
        print("Resampled Actions:", resampled_actions)
        
        initial_state = new_state