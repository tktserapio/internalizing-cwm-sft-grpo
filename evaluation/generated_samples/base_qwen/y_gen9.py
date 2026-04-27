import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import copy

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to create a new state from an existing one
def clone_state(state: State) -> State:
    return copy.deepcopy(state)

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial state with an empty board
    return {
        'board': {},
        'current_player': 0,
        'turn': 0,
        'size': 4,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = clone_state(state)
    new_state['turn'] += 1
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    
    # Convert action string to coordinates
    row, col = map(int, action.split(','))

    # Check if the cell is empty
    if action in new_state['board']:
        raise ValueError(f"Cell {action} is already occupied.")
    
    # Update the board
    new_state['board'][action] = new_state['current_player']
    
    # Check for win condition
    check_win(new_state)
    
    return new_state

def check_win(state: State):
    """
    Checks if there's a winner based on the current state.
    """
    board = state['board']
    size = state['size']
    
    # Define the sides of the board
    side_a_b = set([str(i) for i in range(1, size + 1)])
    side_a_c = set([str(i) for i in range(2, size + 2)])
    side_b_c = set([str(i) for i in range(6, size * 2 + 1)])
    
    # Get the current player's stones
    player_stones = {k: v for k, v in board.items() if v == state['current_player']}
    
    # Check if the player has a connected group touching all three sides
    if len(player_stones) > 0:
        for stone in player_stones.values():
            if stone in side_a_b and stone in side_a_c and stone in side_b_c:
                state['winner'] = state['current_player']
                return
        
    # If no winner, check if the board is full
    if len(board) == size * (size + 1) // 2:
        state['winner'] = None

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return ['Black', 'White'][player_id]

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards.
    """
    if state['winner'] is None:
        return [0.0, 0.0]
    elif state['winner'] == 0:
        return [1.0, 0.0]
    else:
        return [0.0, 1.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    if state['winner'] is not None:
        return []
    
    board = state['board']
    size = state['size']
    
    # Generate all possible moves
    legal_moves = []
    for row in range(size):
        for col in range(1, size * 2 + 1):
            if str(col) not in board:
                legal_moves.append(str(row) + ',' + str(col))
                
    return legal_moves

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    board = state['board']
    size = state['size']
    
    # Create observation for each player
    obs_0 = {k: v for k, v in board.items() if v == 0}
    obs_1 = {k: v for k, v in board.items() if v == 1}
    
    return [obs_0, obs_1]