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
    return {
        'board': [
            ['r', 'n', 'b', 'q', 'k'],
            ['p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K']
        ],
        'current_player': 0,
        'turn_count': 0,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    
    # Parse the action
    piece, from_square, to_square = action.split('_')
    from_file, from_rank = from_square
    to_file, to_rank = to_square
    
    # Convert file and rank to index
    from_index = 5 * (ord(from_file) - ord('a')) + (ord(from_rank) - ord('1'))
    to_index = 5 * (ord(to_file) - ord('a')) + (ord(to_rank) - ord('1'))
    
    # Get the piece at the from square
    piece_at_from = new_state['board'][int(from_rank) - 1][ord(from_file) - ord('a')]
    
    # Update the board
    new_state['board'][int(from_rank) - 1][ord(from_file) - ord('a')] = '.'
    new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = piece_at_from
    
    # Handle special cases like promotion
    if piece == 'P' and abs(int(from_rank) - int(to_rank)) == 2:
        new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = piece.upper()
    
    # Handle castling
    if piece == 'K':
        if from_rank == '1' and to_rank == '5':
            new_state['board'][4][0], new_state['board'][4][4] = new_state['board'][4][4], new_state['board'][4][0]
        elif from_rank == '5' and to_rank == '1':
            new_state['board'][0][0], new_state['board'][0][4] = new_state['board'][0][4], new_state['board'][0][0]
    
    # Update the current player
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    
    # Increment the turn count
    new_state['turn_count'] += 1
    
    return new_state

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

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    winner = state.get('winner')
    if winner == 0:
        return [1.0, 0.0]
    elif winner == 1:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    current_player = state['current_player']
    board = state['board']
    
    # Get all pieces for the current player
    for rank in range(5):
        for file in range(5):
            piece = board[rank][file]
            if piece != '.':
                # Get possible moves for each piece
                if piece.islower():
                    piece = piece.upper()
                
                if piece == 'P':
                    # Pawn movement
                    if current_player == 0 and rank == 1:
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file + ord('a') + 1)}")
                    elif current_player == 1 and rank == 4:
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file + ord('a') + 1)}")
                    if rank > 1 and board[rank - 1][file] == '.':
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file + ord('a'))}")
                    if rank < 4 and board[rank + 1][file] == '.':
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file + ord('a')) + 1}")
                    if rank > 1 and board[rank - 1][file + 1] == '.':
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file + ord('a') + 1)}_Q")
                    if rank > 1 and board[rank - 1][file - 1] == '.':
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file)}_Q")
                elif piece == 'R':
                    # Rook movement
                    for i in range(5):
                        if board[rank][i] == '.':
                            legal_actions.append(f"{piece}_{chr(file + ord('a'))}_{chr(i + ord('a'))}")
                        if board[i][file] == '.':
                            legal_actions.append(f"{piece}_{chr(i + ord('a'))}_{chr(file + ord('a'))}")
                elif piece == 'N':
                    # Knight movement
                    for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
                        nx, ny = file + dx, rank + dy
                        if 0 <= nx < 5 and 0 <= ny < 5:
                            if board[ny][nx] == '.':
                                legal_actions.append(f"{piece}_{chr(file + ord('a'))}_{chr(nx + ord('a'))}")
                            elif board[ny][nx].islower():
                                legal_actions.append(f"{piece}_{chr(file + ord('a'))}_{chr(nx + ord('a'))}_Q")
                elif piece == 'B':
                    # Bishop movement
                    for i in range(5):
                        if board[rank][i] == '.':
                            legal_actions.append(f"{piece}_{chr(file + ord('a'))}_{chr(i + ord('a'))}")
                        if board[i][file] == '.':
                            legal_actions.append(f"{piece}_{chr(i + ord('a'))}_{chr(file + ord('a'))}")
                        if board[rank + i][file + i] == '.':
                            legal_actions.append(f"{piece}_{chr(file + ord('a'))}_{chr(file + ord('a') + i)}")
                        if board[rank + i][file - i] == '.':
                            legal_actions.append(f"{piece}_{chr(file + ord('a'))}_{chr(file - i + ord('a'))}")
                elif piece == 'Q':
                    # Queen movement
                    for i in range(5):
                        if board[rank][i] == '.':
                            legal_actions.append(f"{piece}_{chr(file + ord('a'))}_{chr(i + ord('a'))}")
                        if board[i][file] == '.':
                            legal_actions.append(f"{piece}_{chr(i + ord('a'))}_{chr(file + ord('a'))}")
                        if board[rank + i][file + i] == '.':
                            legal_actions.append(f"{piece}_{chr(file + ord('a'))}_{chr(file + ord('a') + i)}")
                        if board[rank + i][file - i] == '.':
                            legal_actions.append(f"{piece}_{chr(file + ord('a'))}_{chr(file - i + ord('a'))}")
                elif piece == 'K':
                    # King movement
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                        nx, ny = file + dx, rank + dy
                        if 0 <= nx < 5 and 0 <= ny < 5:
                            if board[ny][nx] == '.':
                                legal_actions.append(f"{piece}_{chr(file + ord('a'))}_{chr(nx + ord('a'))}")
                            elif board[ny][nx].islower():
                                legal_actions.append(f"{piece}_{chr(file + ord('a'))}_{chr(nx + ord('a'))}_Q")
                elif piece == 'P':
                    # Pawn promotion
                    if current_player == 0 and rank == 1:
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file + ord('a'))}_Q")
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file + ord('a'))}_R")
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file + ord('a'))}_B")
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file + ord('a'))}_N")
                    elif current_player == 1 and rank == 4:
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file + ord('a'))}_Q")
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file + ord('a'))}_R")
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file + ord('a'))}_B")
                        legal_actions.append(f"P_{chr(file + ord('a'))}_{chr(file + ord('a'))}_N")
                
                # Castling
                if piece == 'K' and board[rank][file] == 'K' and board[rank][file + 1] == '.' and board[rank][file + 2] == '.':
                    legal_actions.append(f"K_{chr(file + ord('a'))}_{chr(file + ord('a') + 2)}")
                if piece == 'K' and board[rank][file] == 'K' and board[rank][file - 1] == '.' and board[rank][file - 2] == '.':
                    legal_actions.append(f"K_{chr(file + ord('a'))}_{chr(file)}")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {
        'board': state['board'],
        'current_player': state['current_player'],
        'turn_count': state['turn_count'],
        'winner': state['winner']
    }
    player_1_obs = {
        'board': state['board'],
        'current_player': state['current_player'],
        'turn_count': state['turn_count'],
        'winner': state['winner']
    }
    return [player_0_obs, player_1_obs]