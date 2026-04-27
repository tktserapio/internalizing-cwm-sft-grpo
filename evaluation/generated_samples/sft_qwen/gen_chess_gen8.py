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

# Helper function to convert file and rank to algebraic notation
def convert_to_algebraic(file: str, rank: int) -> str:
    return f"{file}{rank}"

# Initial state setup
def get_initial_state() -> State:
    # Initialize the state dictionary
    state = {
        'board': [
            ['r', 'n', 'b', 'q', 'k'],
            ['p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K']
        ],
        'turn': 0,
        'winner': None,
        'running_reward': [0.0, 0.0],
        'legal_actions': []
    }
    return state

# Apply action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert action into a tuple of (from_square, to_square)
    from_square, to_square = action.split('_')
    from_square = convert_to_algebraic(from_square[0], int(from_square[1]))
    to_square = convert_to_algebraic(to_square[0], int(to_square[1]))

    # Create a deep copy of the state to avoid mutating the original
    new_state = copy.deepcopy(state)

    # Update the board based on the action
    if action.endswith('_Q'):  # Promotion
        piece, from_square, to_square, promoted_piece = action.split('_')
        new_state['board'][int(to_square[1])][ord(to_square[0]) - ord('a')] = promoted_piece
    else:
        new_state['board'][int(to_square[1])][ord(to_square[0]) - ord('a')] = new_state['board'][int(from_square[1])][ord(from_square[0]) - ord('a')]
        new_state['board'][int(from_square[1])][ord(from_square[0]) - ord('a')] = '.'

    # Update the turn and winner if necessary
    new_state['turn'] = (new_state['turn'] + 1) % 2
    new_state['winner'] = determine_winner(new_state)

    # Determine legal actions for the new state
    new_state['legal_actions'] = get_legal_actions(new_state)

    return new_state

# Determine the winner of the game
def determine_winner(state: State) -> int:
    # Check for checkmate or stalemate
    if not state['legal_actions']:
        return state['turn']
    return None

# Get the current player
def get_current_player(state: State) -> int:
    return state['turn']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    return state['running_reward']

# Get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    # Observations are identical for both players in a perfect information game
    observation = {
        'board': state['board'],
        'turn': state['turn'],
        'winner': state['winner'],
        'legal_actions': state['legal_actions']
    }
    return [observation, observation]

# Get legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    # Implement logic to generate legal actions based on the current state
    # This is a placeholder implementation
    legal_actions = []
    for rank in range(5):
        for file in 'abcde':
            square = convert_to_algebraic(file, rank)
            piece = state['board'][rank][ord(file) - ord('a')]
            if piece != '.':
                if piece == 'P' and rank == 4:
                    # Pawn promotion
                    for piece_type in 'QRBN':
                        legal_actions.append(f"P_{square}_{square}_{piece_type}")
                elif piece == 'P' and rank == 1:
                    # Pawn move
                    if state['board'][rank + 1][ord(file) - ord('a')] == '.':
                        legal_actions.append(f"P_{square}_{convert_to_algebraic(file, rank + 1)}")
                    elif state['board'][rank + 1][ord(file) - ord('a')] != '.' and state['board'][rank + 1][ord(file) - ord('a')].lower() != piece.lower():
                        legal_actions.append(f"P_{square}_{convert_to_algebraic(file, rank + 1)}_Q")  # Promotion to Queen
                elif piece == 'R':
                    # Rook movement
                    for next_rank in range(rank + 1, 5):
                        if state['board'][next_rank][ord(file) - ord('a')] == '.':
                            legal_actions.append(f"R_{square}_{convert_to_algebraic(file, next_rank)}")
                        elif state['board'][next_rank][ord(file) - ord('a')] != '.':
                            break
                    for next_rank in range(rank - 1, -1, -1):
                        if state['board'][next_rank][ord(file) - ord('a')] == '.':
                            legal_actions.append(f"R_{square}_{convert_to_algebraic(file, next_rank)}")
                        elif state['board'][next_rank][ord(file) - ord('a')] != '.':
                            break
                    for next_file in 'abcde':
                        if next_file != file:
                            if state['board'][rank][ord(next_file) - ord('a')] == '.':
                                legal_actions.append(f"R_{square}_{convert_to_algebraic(next_file, rank)}")
                            elif state['board'][rank][ord(next_file) - ord('a')] != '.':
                                break
                    for prev_file in 'abcde':
                        if prev_file != file:
                            if state['board'][rank][ord(prev_file) - ord('a')] == '.':
                                legal_actions.append(f"R_{square}_{convert_to_algebraic(prev_file, rank)}")
                            elif state['board'][rank][ord(prev_file) - ord('a')] != '.':
                                break
                elif piece == 'N':
                    # Knight movement
                    for next_rank, next_file in [(rank + 2, file + 1), (rank + 2, file - 1), (rank - 2, file + 1), (rank - 2, file - 1),
                                                 (rank + 1, file + 2), (rank + 1, file - 2), (rank - 1, file + 2), (rank - 1, file - 2)]:
                        if 0 <= next_rank < 5 and 'abcde'.find(next_file) >= 0:
                            if state['board'][next_rank][ord(next_file) - ord('a')] == '.':
                                legal_actions.append(f"N_{square}_{convert_to_algebraic(next_file, next_rank)}")
                            elif state['board'][next_rank][ord(next_file) - ord('a')] != '.':
                                break
                elif piece == 'B':
                    # Bishop movement
                    for next_rank, next_file in zip(range(rank + 1, 5), 'abcde'):
                        if state['board'][next_rank][ord(next_file) - ord('a')] == '.':
                            legal_actions.append(f"B_{square}_{convert_to_algebraic(next_file, next_rank)}")
                        elif state['board'][next_rank][ord(next_file) - ord('a')] != '.':
                            break
                    for next_rank, next_file in zip(range(rank - 1, -1, -1), 'abcde'):
                        if state['board'][next_rank][ord(next_file) - ord('a')] == '.':
                            legal_actions.append(f"B_{square}_{convert_to_algebraic(next_file, next_rank)}")
                        elif state['board'][next_rank][ord(next_file) - ord('a')] != '.':
                            break
                    for next_rank, next_file in zip(range(rank + 1, 5), reversed('abcde')):
                        if state['board'][next_rank][ord(next_file) - ord('a')] == '.':
                            legal_actions.append(f"B_{square}_{convert_to_algebraic(next_file, next_rank)}")
                        elif state['board'][next_rank][ord(next_file) - ord('a')] != '.':
                            break
                    for next_rank, next_file in zip(range(rank - 1, -1, -1), reversed('abcde')):
                        if state['board'][next_rank][ord(next_file) - ord('a')] == '.':
                            legal_actions.append(f"B_{square}_{convert_to_algebraic(next_file, next_rank)}")
                        elif state['board'][next_rank][ord(next_file) - ord('a')] != '.':
                            break
                elif piece == 'Q':
                    # Queen movement
                    for next_rank, next_file in zip(range(rank + 1, 5), 'abcde'):
                        if state['board'][next_rank][ord(next_file) - ord('a')] == '.':
                            legal_actions.append(f"Q_{square}_{convert_to_algebraic(next_file, next_rank)}")
                        elif state['board'][next_rank][ord(next_file) - ord('a')] != '.':
                            break
                    for next_rank, next_file in zip(range(rank - 1, -1, -1), 'abcde'):
                        if state['board'][next_rank][ord(next_file) - ord('a')] == '.':
                            legal_actions.append(f"Q_{square}_{convert_to_algebraic(next_file, next_rank)}")
                        elif state['board'][next_rank][ord(next_file) - ord('a')] != '.':
                            break
                    for next_rank, next_file in zip(range(rank + 1, 5), reversed('abcde')):
                        if state['board'][next_rank][ord(next_file) - ord('a')] == '.':
                            legal_actions.append(f"Q_{square}_{convert_to_algebraic(next_file, next_rank)}")
                        elif state['board'][next_rank][ord(next_file) - ord('a')] != '.':
                            break
                    for next_rank, next_file in zip(range(rank - 1, -1, -1), reversed('abcde')):
                        if state['board'][next_rank][ord(next_file) - ord('a')] == '.':
                            legal_actions.append(f"Q_{square}_{convert_to_algebraic(next_file, next_rank)}")
                        elif state['board'][next_rank][ord(next_file) - ord('a')] != '.':
                            break
                elif piece == 'K':
                    # King movement
                    for next_rank, next_file in [(rank + 1, file), (rank - 1, file), (rank, file + 1), (rank, file - 1),
                                                 (rank + 1, file + 1), (rank + 1, file - 1), (rank - 1, file + 1), (rank - 1, file - 1)]:
                        if 0 <= next_rank < 5 and 'abcde'.find(next_file) >= 0:
                            if state['board'][next_rank][ord(next_file) - ord('a')] == '.':
                                legal_actions.append(f"K_{square}_{convert_to_algebraic(next_file, next_rank)}")
                            elif state['board'][next_rank][ord(next_file) - ord('a')] != '.':
                                break
    return legal_actions