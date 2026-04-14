import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial state: empty board
    return {
        'board': {},
        'current_player': 0,
        'turn': 0,
        'winner': -4
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    new_state['turn'] += 1
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    
    # Parse the action
    row, col = map(int, action.split(','))

    # Update the board
    new_state['board'][f'{row},{col}'] = new_state['current_player']
    
    # Check for win condition
    if check_win(new_state):
        new_state['winner'] = new_state['current_player']
    
    return new_state

def check_win(state: State) -> bool:
    """
    Checks if there's a winning move based on the current state.
    """
    board = state['board']
    current_player = state['current_player']

    # Define the sides
    side_a_b = set([int(cell) for cell in board if cell.startswith('0,')])
    side_a_c = set([int(cell) for cell in board if cell.startswith('1,')])
    side_b_c = set([int(cell) for cell in board if cell.startswith('2,')])
    
    # Check if the current player can form a winning connection
    if len(side_a_b.intersection(board)) >= 3:
        return True
    elif len(side_a_c.intersection(board)) >= 3:
        return True
    elif len(side_b_c.intersection(board)) >= 3:
        return True
    else:
        return False

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['winner'] if state['winner'] != -4 else state['current_player']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards.
    """
    winner = state['winner']
    return [1.0 if winner == 0 else 0.0, 1.0 if winner == 1 else 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    board = state['board']
    current_player = state['current_player']
    
    # Generate all possible moves
    legal_moves = []
    for row in range(3):
        for col in range(4):
            if f'{row},{col}' not in board:
                legal_moves.append(f'{row},{col}')
    
    # Filter out moves that would result in a win for the opponent
    for move in legal_moves[:]:
        new_board = board.copy()
        new_board[f'{row},{col}'] = current_player
        if check_win(new_board):
            legal_moves.remove(move)
    
    return legal_moves

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    board = state['board']
    observations = [
        {'board': board, 'current_player': state['current_player'], 'turn': state['turn']},
        {'board': board, 'current_player': state['current_player'], 'turn': state['turn']}
    ]
    return observations