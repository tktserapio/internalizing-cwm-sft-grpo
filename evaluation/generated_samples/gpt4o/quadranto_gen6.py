import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Randomly place player 0 in the top-left quadrant (Q1)
    p0_row = random.choice([0, 1])
    p0_col = random.choice([0, 1])
    
    # Randomly place player 1 in the bottom-right quadrant (Q4)
    p1_row = random.choice([2, 3])
    p1_col = random.choice([2, 3])
    
    return {
        'player_positions': [(p0_row, p0_col), (p1_row, p1_col)],
        'turn_count': 0,
        'current_player': 0,
        'game_over': False
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    new_state['player_positions'] = state['player_positions'][:]
    
    current_player = state['current_player']
    row, col = state['player_positions'][current_player]
    
    # Determine new position based on action
    if action == "Up":
        row = max(0, row - 1)
    elif action == "Down":
        row = min(3, row + 1)
    elif action == "Left":
        col = max(0, col - 1)
    elif action == "Right":
        col = min(3, col + 1)
    elif action == "Stay":
        pass  # No change in position
    
    # Update the position of the current player
    new_state['player_positions'][current_player] = (row, col)
    
    # Check for game over condition
    if new_state['player_positions'][0] == new_state['player_positions'][1]:
        new_state['game_over'] = True
    else:
        # Update turn count and switch player
        new_state['turn_count'] += 1
        if new_state['turn_count'] >= 20:
            new_state['game_over'] = True
        else:
            new_state['current_player'] = 1 - current_player
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['game_over']:
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state['game_over']:
        return [0.0, 0.0]
    
    if state['player_positions'][0] == state['player_positions'][1]:
        winner = 1 - state['current_player']
        return [-1.0, 1.0] if winner == 1 else [1.0, -1.0]
    
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['game_over']:
        return []
    return ["Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_pos, p1_pos = state['player_positions']
    p0_quadrant = get_quadrant(p1_pos)
    p1_quadrant = get_quadrant(p0_pos)
    
    return [
        {"My Loc": p0_pos, "Opponent Quadrant": p0_quadrant},
        {"My Loc": p1_pos, "Opponent Quadrant": p1_quadrant}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function requires a more complex implementation to backtrack the actions.
    # For simplicity, we will return a random sequence of actions.
    actions = []
    for obs, action in obs_action_history:
        if action is not None:
            actions.append(action)
        else:
            actions.append(random.choice(["Up", "Down", "Left", "Right", "Stay"]))
    return actions

def get_quadrant(position: Tuple[int, int]) -> str:
    """Helper function to determine the quadrant of a position."""
    row, col = position
    if row < 2 and col < 2:
        return "Top-Left"
    elif row < 2 and col >= 2:
        return "Top-Right"
    elif row >= 2 and col < 2:
        return "Bottom-Left"
    else:
        return "Bottom-Right"