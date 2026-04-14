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

# Helper function to convert algebraic coordinates to board indices
def algebraic_to_board_index(file: str, rank: int) -> tuple[int, int]:
    file_index = ord(file) - ord('a')
    rank_index = 5 - rank
    return file_index, rank_index

# Function to convert board indices to algebraic coordinates
def board_index_to_algebraic(index: tuple[int, int]) -> str:
    file_index, rank_index = index
    file = chr(file_index + ord('a'))
    rank = 5 - rank_index
    return f"{file}{rank}"

# Function to get the initial game state
def get_initial_state() -> State:
    # Initialize the board with pieces
    board = {
        'r': (0, 0), 'n': (0, 1), 'b': (0, 2), 'q': (0, 3), 'k': (0, 4),
        'p': [(1, i) for i in range(5)],
        'R': (4, 0), 'N': (4, 1), 'B': (4, 2), 'Q': (4, 3), 'K': (4, 4),
        'P': [(3, i) for i in range(5)]
    }
    return {'board': board}

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Parse the action
    piece, from_file, from_rank, to_file, to_rank = action.split('_')
    from_file, from_rank = algebraic_to_board_index(from_file, int(from_rank))
    to_file, to_rank = algebraic_to_board_index(to_file, int(to_rank))

    # Get the current board state
    board = state['board']
    
    # Check if the move is valid
    if piece == 'P':
        if from_rank == 1 and to_rank == 2 and board[from_file, from_rank][0] == 'P':
            # Promotion
            promotion_piece = input("Choose promotion piece (Q/R/B/N): ").upper()
            new_board = copy.deepcopy(board)
            new_board[to_file, to_rank] = (promotion_piece, board[from_file, from_rank][1])
            return {'board': new_board}
        else:
            # Regular pawn move
            if board[from_file, from_rank][0] == 'P' and (to_rank == from_rank + 1 or (from_rank == 2 and to_rank == from_rank + 2)):
                new_board = copy.deepcopy(board)
                new_board[to_file, to_rank] = (new_board[from_file, from_rank][0], new_board[from_file, from_rank][1])
                new_board[from_file, from_rank] = ('.', 0)
                return {'board': new_board}
            else:
                return state
    elif piece == 'R':
        if board[from_file, from_rank][0] == 'R':
            new_board = copy.deepcopy(board)
            new_board[to_file, to_rank] = (new_board[from_file, from_rank][0], new_board[from_file, from_rank][1])
            new_board[from_file, from_rank] = ('.', 0)
            return {'board': new_board}
        else:
            return state
    elif piece == 'N':
        if board[from_file, from_rank][0] == 'N':
            new_board = copy.deepcopy(board)
            new_board[to_file, to_rank] = (new_board[from_file, from_rank][0], new_board[from_file, from_rank][1])
            new_board[from_file, from_rank] = ('.', 0)
            return {'board': new_board}
        else:
            return state
    elif piece == 'B':
        if board[from_file, from_rank][0] == 'B':
            new_board = copy.deepcopy(board)
            new_board[to_file, to_rank] = (new_board[from_file, from_rank][0], new_board[from_file, from_rank][1])
            new_board[from_file, from_rank] = ('.', 0)
            return {'board': new_board}
        else:
            return state
    elif piece == 'Q':
        if board[from_file, from_rank][0] == 'Q':
            new_board = copy.deepcopy(board)
            new_board[to_file, to_rank] = (new_board[from_file, from_rank][0], new_board[from_file, from_rank][1])
            new_board[from_file, from_rank] = ('.', 0)
            return {'board': new_board}
        else:
            return state
    elif piece == 'K':
        if board[from_file, from_rank][0] == 'K':
            new_board = copy.deepcopy(board)
            new_board[to_file, to_rank] = (new_board[from_file, from_rank][0], new_board[from_file, from_rank][1])
            new_board[from_file, from_rank] = ('.', 0)
            return {'board': new_board}
        else:
            return state
    else:
        return state

# Function to get the current player
def get_current_player(state: State) -> int:
    # Determine the current player based on whose turn it is
    board = state['board']
    white_pawns = sum(1 for _, rank in board.items() if rank[0] == 'P' and rank[1] == 1)
    black_pawns = sum(1 for _, rank in board.items() if rank[0] == 'P' and rank[1] == 4)
    if white_pawns > black_pawns:
        return 0
    elif black_pawns > white_pawns:
        return 1
    else:
        return -4

# Function to get the player name
def get_player_name(player_id: int) -> str:
    return ['White', 'Black'][player_id]

# Function to get the rewards per player
def get_rewards(state: State) -> list[float]:
    # Determine the winner based on the current state
    board = state['board']
    white_king = None
    black_king = None
    for _, rank in board.items():
        if rank[0] == 'K' and rank[1] == 1:
            white_king = rank
        elif rank[0] == 'K' and rank[1] == 4:
            black_king = rank
    if white_king and black_king:
        if white_king == black_king:
            return [0.0, 0.0]
        elif white_king[1] == 1 and black_king[1] == 4:
            return [-1.0, 1.0]
        elif white_king[1] == 4 and black_king[1] == 1:
            return [1.0, -1.0]
    return [0.0, 0.0]

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    # Get the current player
    current_player = get_current_player(state)
    if current_player == -4:
        return []  # Terminal state
    else:
        board = state['board']
        legal_actions = []
        for file, rank in board.items():
            if rank[0] != '.':
                piece = rank[0]
                piece_index = board[file, rank[1]]
                if piece == 'P':
                    # Pawn movement
                    if rank[1] == 1:
                        if (file, rank[1] + 1) in board and board[file, rank[1] + 1][0] == '.':
                            legal_actions.append(f"P_{file}_{rank[1]}_{file}_{rank[1] + 1}")
                        if (file, rank[1] + 2) in board and board[file, rank[1] + 2][0] == '.':
                            legal_actions.append(f"P_{file}_{rank[1]}_{file}_{rank[1] + 2}")
                    if rank[1] < 4:
                        if (file, rank[1] + 1) in board and board[file, rank[1] + 1][0] != '.':
                            legal_actions.append(f"P_{file}_{rank[1]}_{file}_{rank[1] + 1}")
                elif piece == 'R':
                    # Rook movement
                    for i in range(1, 5):
                        if (file, rank[1] + i) in board and board[file, rank[1] + i][0] == '.':
                            legal_actions.append(f"R_{file}_{rank[1]}_{file}_{rank[1] + i}")
                        if (file, rank[1] - i) in board and board[file, rank[1] - i][0] == '.':
                            legal_actions.append(f"R_{file}_{rank[1]}_{file}_{rank[1] - i}")
                        if (file + i, rank[1]) in board and board[file + i, rank[1]][0] == '.':
                            legal_actions.append(f"R_{file}_{rank[1]}_{file + i}_{rank[1]}")
                        if (file - i, rank[1]) in board and board[file - i, rank[1]][0] == '.':
                            legal_actions.append(f"R_{file}_{rank[1]}_{file - i}_{rank[1]}")
                elif piece == 'N':
                    # Knight movement
                    for dx, dy in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
                        new_file, new_rank = file + dx, rank[1] + dy
                        if (new_file, new_rank) in board and board[new_file, new_rank][0] == '.':
                            legal_actions.append(f"N_{file}_{rank[1]}_{new_file}_{new_rank}")
                elif piece == 'B':
                    # Bishop movement
                    for i in range(1, 5):
                        if (file + i, rank[1] + i) in board and board[file + i, rank[1] + i][0] == '.':
                            legal_actions.append(f"B_{file}_{rank[1]}_{file + i}_{rank[1] + i}")
                        if (file + i, rank[1] - i) in board and board[file + i, rank[1] - i][0] == '.':
                            legal_actions.append(f"B_{file}_{rank[1]}_{file + i}_{rank[1] - i}")
                        if (file - i, rank[1] + i) in board and board[file - i, rank[1] + i][0] == '.':
                            legal_actions.append(f"B_{file}_{rank[1]}_{file - i}_{rank[1] + i}")
                        if (file - i, rank[1] - i) in board and board[file - i, rank[1] - i][0] == '.':
                            legal_actions.append(f"B_{file}_{rank[1]}_{file - i}_{rank[1] - i}")
                elif piece == 'Q':
                    # Queen movement
                    for i in range(1, 5):
                        if (file + i, rank[1] + i) in board and board[file + i, rank[1] + i][0] == '.':
                            legal_actions.append(f"Q_{file}_{rank[1]}_{file + i}_{rank[1] + i}")
                        if (file + i, rank[1] - i) in board and board[file + i, rank[1] - i][0] == '.':
                            legal_actions.append(f"Q_{file}_{rank[1]}_{file + i}_{rank[1] - i}")
                        if (file - i, rank[1] + i) in board and board[file - i, rank[1] + i][0] == '.':
                            legal_actions.append(f"Q_{file}_{rank[1]}_{file - i}_{rank[1] + i}")
                        if (file - i, rank[1] - i) in board and board[file - i, rank[1] - i][0] == '.':
                            legal_actions.append(f"Q_{file}_{rank[1]}_{file - i}_{rank[1] - i}")
                        if (file, rank[1] + i) in board and board[file, rank[1] + i][0] == '.':
                            legal_actions.append(f"Q_{file}_{rank[1]}_{file}_{rank[1] + i}")
                        if (file, rank[1] - i) in board and board[file, rank[1] - i][0] == '.':
                            legal_actions.append(f"Q_{file}_{rank[1]}_{file}_{rank[1] - i}")
                        if (file + i, rank[1]) in board and board[file + i, rank[1]][0] == '.':
                            legal_actions.append(f"Q_{file}_{rank[1]}_{file + i}_{rank[1]}")
                        if (file - i, rank[1]) in board and board[file - i, rank[1]][0] == '.':
                            legal_actions.append(f"Q_{file}_{rank[1]}_{file - i}_{rank[1]}")
                elif piece == 'K':
                    # King movement
                    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                        new_file, new_rank = file + dx, rank[1] + dy
                        if (new_file, new_rank) in board and board[new_file, new_rank][0] == '.':
                            legal_actions.append(f"K_{file}_{rank[1]}_{new_file}_{new_rank}")
        return legal_actions

# Function to get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    # Get the current player
    current_player = get_current_player(state)
    if current_player == -4:
        return [{}, {}]  # Terminal state
    else:
        board = state['board']
        player_0_obs = {}
        player_1_obs = {}
        for file, rank in board.items():
            if rank[0] != '.':
                piece = rank[0]
                piece_index = board[file, rank[1]]
                if piece == 'P':
                    player_0_obs[f"P_{file}_{rank[1]}"] = 1
                elif piece == 'R':
                    player_0_obs[f"R_{file}_{rank[1]}"] = 1
                elif piece == 'N':
                    player_0_obs[f"N_{file}_{rank[1]}"] = 1
                elif piece == 'B':
                    player_0_obs[f"B_{file}_{rank[1]}"] = 1
                elif piece == 'Q':
                    player_0_obs[f"Q_{file}_{rank[1]}"] = 1
                elif piece == 'K':
                    player_0_obs[f"K_{file}_{rank[1]}"] = 1
                if piece == 'P':
                    player_1_obs[f"P_{file}_{rank[1]}"] = 1
                elif piece == 'R':
                    player_1_obs[f"R_{file}_{rank[1]}"] = 1
                elif piece == 'N':
                    player_1_obs[f"N_{file}_{rank[1]}"] = 1
                elif piece == 'B':
                    player_1_obs[f"B_{file}_{rank[1]}"] = 1
                elif piece == 'Q':
                    player_1_obs[f"Q_{file}_{rank[1]}"] = 1
                elif piece == 'K':
                    player_1_obs[f"K_{file}_{rank[1]}"] = 1
        return [player_0_obs, player_1_obs]