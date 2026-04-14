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
    # Initialize the state dictionary
    state = {
        'board': {
            'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K',
            'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P',
            'a3': '.', 'b3': '.', 'c3': '.', 'd3': '.', 'e3': '.',
            'a4': '.', 'b4': '.', 'c4': '.', 'd4': '.', 'e4': '.',
            'a5': 'r', 'b5': 'n', 'c5': 'b', 'd5': 'q', 'e5': 'k'
        },
        'turn': 0,
        'winner': None,
        'running_reward': [0.0, 0.0]
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    
    # Parse the action
    piece, from_square, to_square = action.split('_')
    from_square = from_square.lower()
    to_square = to_square.lower()

    # Get the current player
    current_player = state['turn']
    
    # Validate the action
    if not validate_action(new_state, piece, from_square, to_square):
        raise ValueError("Invalid action")
    
    # Perform the move
    perform_move(new_state, piece, from_square, to_square)
    
    # Update the turn
    new_state['turn'] = (current_player + 1) % 2
    
    # Determine the winner
    winner = determine_winner(new_state)
    if winner:
        new_state['winner'] = winner
        new_state['running_reward'] = [1.0, -1.0] if winner == 0 else [-1.0, 1.0]
    
    return new_state

def validate_action(state: State, piece: str, from_square: str, to_square: str) -> bool:
    """
    Validates the action based on the current state and the rules of the game.
    """
    # Check if the piece exists at the from_square
    if from_square not in state['board']:
        return False
    
    # Check if the to_square is within the board bounds
    if to_square not in state['board']:
        return False
    
    # Check if the piece matches the given piece
    if state['board'][from_square] != piece:
        return False
    
    # Additional validation logic can be added here
    return True

def perform_move(state: State, piece: str, from_square: str, to_square: str) -> None:
    """
    Performs the move on the board.
    """
    # Remove the piece from the from_square
    state['board'][from_square] = '.'
    
    # Place the piece at the to_square
    state['board'][to_square] = piece

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['turn']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    return state['running_reward']

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    # Implement logic to generate legal actions
    # This is a placeholder for now
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    # Placeholder for observations
    return [{'board': state['board'], 'turn': state['turn']} for _ in range(2)]