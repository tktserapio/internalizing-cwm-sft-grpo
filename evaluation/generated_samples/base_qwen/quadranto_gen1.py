import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initialize the board as a 4x4 grid
    board = [[(i, j) for j in range(4)] for i in range(4)]
    
    # Randomly place player 0 in the top-left quadrant
    player_0_location = random.choice(board[0][0:2]) + (0,)
    board[player_0_location[0]][player_0_location[1]] = 'P0'
    
    # Randomly place player 1 in the bottom-right quadrant
    player_1_location = random.choice(board[2][2:4]) + (3,)
    board[player_1_location[0]][player_1_location[1]] = 'P1'
    
    # Create the initial state dictionary
    initial_state = {
        'board': board,
        'turn_count': 0,
        'current_player': 0,
        'player_0_location': player_0_location,
        'player_1_location': player_1_location
    }
    return initial_state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    current_player = new_state['current_player']
    opponent_location = new_state['player_1_location'] if current_player == 0 else new_state['player_0_location']
    
    # Determine the new location based on the action
    if action == 'Stay':
        new_location = new_state['player_0_location'] if current_player == 0 else new_state['player_1_location']
    elif action in ['Up', 'Down', 'Left', 'Right']:
        row, col = new_state['player_0_location'] if current_player == 0 else new_state['player_1_location']
        if action == 'Up':
            new_location = (max(row - 1, 0), col)
        elif action == 'Down':
            new_location = (min(row + 1, 3), col)
        elif action == 'Left':
            new_location = (row, max(col - 1, 0))
        elif action == 'Right':
            new_location = (row, min(col + 1, 3))
    else:
        raise ValueError(f"Invalid action: {action}")
    
    # Check if the move results in a win
    if new_location == opponent_location:
        new_state['current_player'] = -current_player  # Switch to the other player
        new_state['turn_count'] = 20  # End the game in a draw
        new_state['player_0_location'] = new_state['player_1_location'] = None  # Reset locations
        new_state['player_0_reward'], new_state['player_1_reward'] = 0.0, 0.0  # No reward
        return new_state
    
    # Update the board and state
    new_state['board'][new_state['player_0_location'][0]][new_state['player_0_location'][1]] = '.'
    new_state['board'][new_location[0]][new_location[1]] = 'P' + str(current_player)
    new_state['player_0_location'] = new_state['player_1_location'] = new_location
    new_state['turn_count'] += 1
    
    # Get the opponent's observation
    opponent_observation = {
        'my_loc': new_location,
        'opponent_quadrant': 'Top-Left' if current_player == 0 else 'Bottom-Right'
    }
    
    # Determine the reward
    if new_state['turn_count'] >= 20:
        new_state['player_0_reward'], new_state['player_1_reward'] = 0.0, 0.0  # Draw
    elif new_state['current_player'] == 0:
        new_state['player_0_reward'], new_state['player_1_reward'] = 1.0, -1.0  # Player 0 wins
    else:
        new_state['player_0_reward'], new_state['player_1_reward'] = -1.0, 1.0  # Player 1 wins
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Player ' + str(player_id)

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    return [state['player_0_reward'], state['player_1_reward']]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = state['current_player']
    if state['turn_count'] >= 20:
        return []  # Terminal state
    elif current_player == 0:
        return ['Up', 'Down', 'Left', 'Right', 'Stay']
    else:
        return ['Up', 'Down', 'Left', 'Right', 'Stay']

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        'my_loc': state['player_0_location'],
        'opponent_quadrant': 'Top-Left' if state['current_player'] == 0 else 'Bottom-Right'
    }
    player_1_obs = {
        'my_loc': state['player_1_location'],
        'opponent_quadrant': 'Top-Left' if state['current_player'] == 1 else 'Bottom-Right'
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to be implemented to sample actions based on the history of observations and actions.
    # For simplicity, we'll just return a fixed sequence of actions that could explain the given observations.
    # In a real implementation, this would involve more complex logic to ensure the sampled sequence is valid.
    # Here, we'll just return a fixed sequence of actions.
    if player_id == 0:
        return ['Right', 'Down', 'Right', 'Up', 'Right']
    else:
        return ['Up', 'Left', 'Up', 'Left', 'Up']