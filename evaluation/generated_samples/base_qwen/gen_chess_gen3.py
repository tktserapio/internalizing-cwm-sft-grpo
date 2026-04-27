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

# Helper function to convert coordinates to a unique key
def coord_to_key(rank: int, file: str) -> str:
    return f"{file}{rank}"

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial board setup
    initial_board = {
        coord_to_key(1, 'a'): 'R', coord_to_key(1, 'b'): 'N', coord_to_key(1, 'c'): 'B', 
        coord_to_key(1, 'd'): 'Q', coord_to_key(1, 'e'): 'K',
        coord_to_key(2, 'a'): 'P', coord_to_key(2, 'b'): 'P', coord_to_key(2, 'c'): 'P', 
        coord_to_key(2, 'd'): 'P', coord_to_key(2, 'e'): 'P',
        coord_to_key(4, 'a'): 'r', coord_to_key(4, 'b'): 'n', coord_to_key(4, 'c'): 'b', 
        coord_to_key(4, 'd'): 'q', coord_to_key(4, 'e'): 'k',
        coord_to_key(5, 'a'): '.', coord_to_key(5, 'b'): '.', coord_to_key(5, 'c'): '.', 
        coord_to_key(5, 'd'): '.', coord_to_key(5, 'e'): '.'
    }
    return initial_board

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy.deepcopy(state)
    
    # Parse the action
    piece, from_rank, from_file, to_rank, to_file, promo = parse_action(action)
    
    # Update the board
    from_key = coord_to_key(int(from_rank), from_file)
    to_key = coord_to_key(int(to_rank), to_file)
    new_state[to_key] = new_state[from_key]
    del new_state[from_key]
    
    # Handle promotion
    if promo:
        new_state[to_key] = promo
    
    # Determine the current player
    current_player = get_current_player(new_state)
    
    return new_state

def parse_action(action: Action) -> tuple[str, int, str, int, str, str]:
    """
    Parses the action string into its components.
    """
    pieces = {'P': 'p', 'N': 'n', 'B': 'b', 'R': 'r', 'Q': 'q', 'K': 'k'}
    promo_pieces = {'Q': 'q', 'R': 'r', 'B': 'b', 'N': 'n'}
    
    piece, from_rank, from_file, to_rank, to_file, promo = action.split('_')
    from_rank, from_file = from_rank, from_file
    to_rank, to_file = to_rank, to_file
    if promo:
        promo = promo_pieces[promo]
    
    return pieces[piece], from_rank, from_file, to_rank, to_file, promo

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    # Determine the current player based on whose turn it is
    for rank in state.values():
        if rank == 'K':
            return 0 if rank == 'K' else 1
    return -4

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    # Determine the winner
    white_king = 'K' in state.values()
    black_king = 'k' in state.values()
    
    if white_king and not black_king:
        return [1.0, -1.0]
    elif black_king and not white_king:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    
    # Get the current player
    current_player = get_current_player(state)
    
    # Iterate over each square in the state
    for rank in state.keys():
        for file in state[rank]:
            piece = state[rank]
            
            # Get possible moves for the piece
            if piece == 'P':
                # Pawn movement
                if current_player == 0:
                    if state[f"{file}{int(rank)+1}"] == '.':
                        legal_actions.append(f"P_{rank}_{int(rank)+1}")
                    if state[f"{file}{int(rank)+2}"] == '.' and state[f"{file}{int(rank)+1}"] == '.':
                        legal_actions.append(f"P_{rank}_{int(rank)+2}")
                    if state[f"{file}{int(rank)+1}"] != '.' and state[f"{file}{int(rank)+1}"].islower():
                        legal_actions.append(f"P_{rank}_{int(rank)+1}_Q")
                else:
                    if state[f"{file}{int(rank)-1}"] == '.':
                        legal_actions.append(f"P_{rank}_{int(rank)-1}")
                    if state[f"{file}{int(rank)-2}"] == '.' and state[f"{file}{int(rank)-1}"] == '.':
                        legal_actions.append(f"P_{rank}_{int(rank)-2}")
                    if state[f"{file}{int(rank)-1}"] != '.' and state[f"{file}{int(rank)-1}"].isupper():
                        legal_actions.append(f"P_{rank}_{int(rank)-1}_Q")
                
                # Capture moves
                if current_player == 0:
                    if state[f"{file}{int(rank)+1}"].islower():
                        legal_actions.append(f"P_{rank}_{int(rank)+1}_Q")
                else:
                    if state[f"{file}{int(rank)-1}"].isupper():
                        legal_actions.append(f"P_{rank}_{int(rank)-1}_Q")
                
            elif piece == 'N':
                # Knight movement
                for move in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
                    new_rank = int(rank) + move[0]
                    new_file = chr(ord(file) + move[1])
                    if 1 <= new_rank <= 5 and 'a' <= new_file <= 'e':
                        if state[f"{new_file}{new_rank}"] == '.':
                            legal_actions.append(f"N_{rank}_{file}_{new_rank}_{new_file}")
                        elif state[f"{new_file}{new_rank}"].isupper() != current_player:
                            legal_actions.append(f"N_{rank}_{file}_{new_rank}_{new_file}_Q")
            
            elif piece == 'B':
                # Bishop movement
                for move in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    new_rank = int(rank) + move[0]
                    new_file = chr(ord(file) + move[1])
                    while 1 <= new_rank <= 5 and 'a' <= new_file <= 'e':
                        if state[f"{new_file}{new_rank}"] == '.':
                            legal_actions.append(f"B_{rank}_{file}_{new_rank}_{new_file}")
                            break
                        elif state[f"{new_file}{new_rank}"].isupper() != current_player:
                            legal_actions.append(f"B_{rank}_{file}_{new_rank}_{new_file}_Q")
                            break
                        break
                
            elif piece == 'R':
                # Rook movement
                for move in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    new_rank = int(rank) + move[0]
                    new_file = chr(ord(file) + move[1])
                    while 1 <= new_rank <= 5 and 'a' <= new_file <= 'e':
                        if state[f"{new_file}{new_rank}"] == '.':
                            legal_actions.append(f"R_{rank}_{file}_{new_rank}_{new_file}")
                            break
                        elif state[f"{new_file}{new_rank}"].isupper() != current_player:
                            legal_actions.append(f"R_{rank}_{file}_{new_rank}_{new_file}_Q")
                            break
                        break
            
            elif piece == 'Q':
                # Queen movement
                for move in [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (0, 1), (-1, 0), (0, -1)]:
                    new_rank = int(rank) + move[0]
                    new_file = chr(ord(file) + move[1])
                    while 1 <= new_rank <= 5 and 'a' <= new_file <= 'e':
                        if state[f"{new_file}{new_rank}"] == '.':
                            legal_actions.append(f"Q_{rank}_{file}_{new_rank}_{new_file}")
                            break
                        elif state[f"{new_file}{new_rank}"].isupper() != current_player:
                            legal_actions.append(f"Q_{rank}_{file}_{new_rank}_{new_file}_Q")
                            break
                        break
            
            elif piece == 'K':
                # King movement
                for move in [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    new_rank = int(rank) + move[0]
                    new_file = chr(ord(file) + move[1])
                    if 1 <= new_rank <= 5 and 'a' <= new_file <= 'e':
                        if state[f"{new_file}{new_rank}"] == '.':
                            legal_actions.append(f"K_{rank}_{file}_{new_rank}_{new_file}")
                        elif state[f"{new_file}{new_rank}"].isupper() != current_player:
                            legal_actions.append(f"K_{rank}_{file}_{new_rank}_{new_file}_Q")
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {coord: piece for coord, piece in state.items() if piece.islower()}
    player_1_obs = {coord: piece for coord, piece in state.items() if piece.isupper()}
    return [player_0_obs, player_1_obs]