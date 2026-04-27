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

# Helper function to convert algebraic notation to coordinates
def algebraic_to_coordinates(algebraic_notation):
    file = algebraic_notation[0]
    rank = 6 - int(algebraic_notation[1])  # Inverting ranks for easier calculation
    return file, rank

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    initial_state = {
        'board': [
            ['r', 'n', 'b', 'q', 'k'],
            ['p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K']
        ],
        'turn': 0,
        'current_player': 0,
        'winner': None,
        'running_reward': [0.0, 0.0],
        'legal_actions': []
    }
    return initial_state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy.deepcopy(state)
    piece, from_square, to_square = action.split('_')
    from_file, from_rank = algebraic_to_coordinates(from_square)
    to_file, to_rank = algebraic_to_coordinates(to_square)
    
    # Update the board
    new_board = copy.deepcopy(state['board'])
    new_board[from_rank][from_file] = state['board'][to_rank][to_file]
    new_board[to_rank][to_file] = state['board'][from_rank][from_file]
    
    # Handle special cases like pawn promotion
    if piece == 'P' and abs(from_rank - to_rank) == 2:
        new_board[to_rank][to_file] = 'Q'
    
    # Update the current player
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    
    # Determine winner based on the new state
    winner = determine_winner(new_board)
    if winner is not None:
        new_state['winner'] = winner
        new_state['running_reward'] = [1.0, -1.0] if winner == 0 else [-1.0, 1.0]
        new_state['legal_actions'] = []
    
    # Update the legal actions
    new_state['legal_actions'] = get_legal_actions(new_state)
    
    return new_state

def determine_winner(board):
    """
    Determines if there is a winner based on the current board configuration.
    """
    # Check for checkmate
    for rank in range(5):
        for file in range(5):
            piece = board[rank][file]
            if piece != '.':
                if piece == 'K':
                    return None
                elif piece == 'Q':
                    return 1 if rank < 3 else 0
                elif piece == 'R':
                    if rank == 0 and file in [0, 4]:  # White rooks
                        return 1
                    elif rank == 4 and file in [0, 4]:  # Black rooks
                        return 0
                elif piece == 'B':
                    if rank == 0 and file in [0, 4]:  # White bishops
                        return 1
                    elif rank == 4 and file in [0, 4]:  # Black bishops
                        return 0
                elif piece == 'N':
                    if rank == 0 and file in [0, 1, 4, 5]:  # White knights
                        return 1
                    elif rank == 4 and file in [0, 1, 4, 5]:  # Black knights
                        return 0
                elif piece == 'P':
                    if rank == 4 and file in [0, 1, 2, 3, 4]:  # White pawns
                        return 1
                    elif rank == 1 and file in [0, 1, 2, 3, 4]:  # Black pawns
                        return 0
    return None

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    return state['running_reward']

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    if state['winner'] is not None:
        return []
    
    legal_actions = []
    for rank in range(5):
        for file in range(5):
            piece = state['board'][rank][file]
            if piece != '.':
                if piece == 'P':
                    if rank == 4 and file in [0, 1, 2, 3, 4]:
                        legal_actions.append(f"P_{file}_{file + 1}")
                    elif rank == 3 and file in [0, 1, 2, 3, 4]:
                        legal_actions.append(f"P_{file}_{file + 1}")
                        legal_actions.append(f"P_{file}_{file + 2}")
                elif piece == 'N':
                    if rank in [0, 4] and file in [0, 1, 4, 5]:
                        legal_actions.append(f"N_{file}_{file + 1}")
                        legal_actions.append(f"N_{file}_{file - 1}")
                        legal_actions.append(f"N_{file + 1}_{file + 2}")
                        legal_actions.append(f"N_{file - 1}_{file + 2}")
                        legal_actions.append(f"N_{file + 1}_{file - 2}")
                        legal_actions.append(f"N_{file - 1}_{file - 2}")
                elif piece == 'B':
                    if rank in [0, 4] and file in [0, 1, 4, 5]:
                        for i in range(1, 5):
                            if file + i < 5 and state['board'][rank][file + i] == '.':
                                legal_actions.append(f"B_{file}_{file + i}")
                            elif file + i < 5 and state['board'][rank][file + i] == 'P':
                                legal_actions.append(f"B_{file}_{file + i}_Q")
                            elif file + i >= 5 and state['board'][rank][file + i - 5] == '.':
                                legal_actions.append(f"B_{file}_{file + i - 5}")
                            elif file + i >= 5 and state['board'][rank][file + i - 5] == 'P':
                                legal_actions.append(f"B_{file}_{file + i - 5}_Q")
                        for i in range(1, 5):
                            if file - i >= 0 and state['board'][rank][file - i] == '.':
                                legal_actions.append(f"B_{file}_{file - i}")
                            elif file - i >= 0 and state['board'][rank][file - i] == 'P':
                                legal_actions.append(f"B_{file}_{file - i}_Q")
                            elif file - i < 0 and state['board'][rank][file + i - 5] == '.':
                                legal_actions.append(f"B_{file}_{file + i - 5}")
                            elif file - i < 0 and state['board'][rank][file + i - 5] == 'P':
                                legal_actions.append(f"B_{file}_{file + i - 5}_Q")
                elif piece == 'R':
                    if rank in [0, 4] and file in [0, 1, 4, 5]:
                        for i in range(1, 5):
                            if file + i < 5 and state['board'][rank][file + i] == '.':
                                legal_actions.append(f"R_{file}_{file + i}")
                            elif file + i < 5 and state['board'][rank][file + i] == 'P':
                                legal_actions.append(f"R_{file}_{file + i}_Q")
                            elif file + i >= 5 and state['board'][rank][file + i - 5] == '.':
                                legal_actions.append(f"R_{file}_{file + i - 5}")
                            elif file + i >= 5 and state['board'][rank][file + i - 5] == 'P':
                                legal_actions.append(f"R_{file}_{file + i - 5}_Q")
                        for i in range(1, 5):
                            if file - i >= 0 and state['board'][rank][file - i] == '.':
                                legal_actions.append(f"R_{file}_{file - i}")
                            elif file - i >= 0 and state['board'][rank][file - i] == 'P':
                                legal_actions.append(f"R_{file}_{file - i}_Q")
                            elif file - i < 0 and state['board'][rank][file + i - 5] == '.':
                                legal_actions.append(f"R_{file}_{file + i - 5}")
                            elif file - i < 0 and state['board'][rank][file + i - 5] == 'P':
                                legal_actions.append(f"R_{file}_{file + i - 5}_Q")
                elif piece == 'Q':
                    if rank in [0, 4] and file in [0, 1, 4, 5]:
                        for i in range(1, 5):
                            if file + i < 5 and state['board'][rank][file + i] == '.':
                                legal_actions.append(f"Q_{file}_{file + i}")
                            elif file + i < 5 and state['board'][rank][file + i] == 'P':
                                legal_actions.append(f"Q_{file}_{file + i}_Q")
                            elif file + i >= 5 and state['board'][rank][file + i - 5] == '.':
                                legal_actions.append(f"Q_{file}_{file + i - 5}")
                            elif file + i >= 5 and state['board'][rank][file + i - 5] == 'P':
                                legal_actions.append(f"Q_{file}_{file + i - 5}_Q")
                        for i in range(1, 5):
                            if file - i >= 0 and state['board'][rank][file - i] == '.':
                                legal_actions.append(f"Q_{file}_{file - i}")
                            elif file - i >= 0 and state['board'][rank][file - i] == 'P':
                                legal_actions.append(f"Q_{file}_{file - i}_Q")
                            elif file - i < 0 and state['board'][rank][file + i - 5] == '.':
                                legal_actions.append(f"Q_{file}_{file + i - 5}")
                            elif file - i < 0 and state['board'][rank][file + i - 5] == 'P':
                                legal_actions.append(f"Q_{file}_{file + i - 5}_Q")
                        for i in range(1, 5):
                            if file + i < 5 and state['board'][rank][file + i] == '.':
                                legal_actions.append(f"Q_{file}_{file + i}")
                            elif file + i < 5 and state['board'][rank][file + i] == 'P':
                                legal_actions.append(f"Q_{file}_{file + i}_Q")
                            elif file + i >= 5 and state['board'][rank][file + i - 5] == '.':
                                legal_actions.append(f"Q_{file}_{file + i - 5}")
                            elif file + i >= 5 and state['board'][rank][file + i - 5] == 'P':
                                legal_actions.append(f"Q_{file}_{file + i - 5}_Q")
                        for i in range(1, 5):
                            if file - i >= 0 and state['board'][rank][file - i] == '.':
                                legal_actions.append(f"Q_{file}_{file - i}")
                            elif file - i >= 0 and state['board'][rank][file - i] == 'P':
                                legal_actions.append(f"Q_{file}_{file - i}_Q")
                            elif file - i < 0 and state['board'][rank][file + i - 5] == '.':
                                legal_actions.append(f"Q_{file}_{file + i - 5}")
                            elif file - i < 0 and state['board'][rank][file + i - 5] == 'P':
                                legal_actions.append(f"Q_{file}_{file + i - 5}_Q")
                elif piece == 'K':
                    if rank in [0, 4] and file in [0, 1, 4, 5]:
                        legal_actions.append(f"K_{file}_{file + 1}")
                        legal_actions.append(f"K_{file}_{file - 1}")
                        legal_actions.append(f"K_{file + 1}_{file + 2}")
                        legal_actions.append(f"K_{file - 1}_{file + 2}")
                        legal_actions.append(f"K_{file + 1}_{file - 2}")
                        legal_actions.append(f"K_{file - 1}_{file - 2}")
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {
        'board': state['board'],
        'turn': state['turn'],
        'current_player': state['current_player'],
        'winner': state['winner'],
        'running_reward': state['running_reward'][0]
    }
    player_1_obs = {
        'board': state['board'],
        'turn': state['turn'],
        'current_player': state['current_player'],
        'winner': state['winner'],
        'running_reward': state['running_reward'][1]
    }
    return [player_0_obs, player_1_obs]