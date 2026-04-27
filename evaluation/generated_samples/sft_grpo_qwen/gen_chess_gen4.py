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
            ['.','.','.','.','.'],
            ['P','P','P','P','P'],
            ['R','N','B','Q','K']
        ],
        'turn': 0,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    piece, from_square, to_square = action.split('_')
    from_file, from_rank = from_square[0], from_square[1]
    to_file, to_rank = to_square[0], to_square[1]

    # Convert file and rank to index
    from_index = (ord(from_file) - ord('a'), int(from_rank) - 1)
    to_index = (ord(to_file) - ord('a'), int(to_rank) - 1)

    # Get the piece at the from_square
    piece_at_from = new_state['board'][from_index[1]][from_index[0]]

    # Update the board
    new_state['board'][from_index[1]][from_index[0]] = '.'
    new_state['board'][to_index[1]][to_index[0]] = piece_at_from

    # Handle pawn movement
    if piece == 'P':
        if new_state['board'][to_index[1]][to_index[0]] == '.':
            new_state['board'][to_index[1]][to_index[0]] = piece_at_from
            new_state['board'][from_index[1]][from_index[0]] = '.'
        else:
            captured_piece = new_state['board'][to_index[1]][to_index[0]]
            new_state['board'][to_index[1]][to_index[0]] = piece_at_from
            new_state['board'][from_index[1]][from_index[0]] = '.'
            new_state['board'][to_index[1] + (1 if to_rank < from_rank else -1)][to_index[0]] = captured_piece

    # Handle promotion
    if piece == 'P' and (to_rank == 0 or to_rank == 4):
        new_state['board'][to_index[1]][to_index[0]] = 'Q'

    # Handle castling
    if piece == 'R' and from_index == (0, 0) and to_index == (0, 2):
        new_state['board'][0][1] = '.'
        new_state['board'][0][3] = 'R'
    elif piece == 'R' and from_index == (0, 7) and to_index == (0, 5):
        new_state['board'][0][6] = '.'
        new_state['board'][0][4] = 'R'

    # Handle en passant
    if piece == 'P' and abs(int(to_rank) - int(from_rank)) == 2:
        captured_piece = new_state['board'][int((int(to_rank) + int(from_rank)) / 2)][int(to_file)]
        new_state['board'][int((int(to_rank) + int(from_rank)) / 2)][int(to_file)] = '.'
        new_state['board'][int(from_rank)][int(to_file)] = captured_piece

    # Update turn
    new_state['turn'] = 1 - new_state['turn']

    return new_state

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
    winner = state['winner']
    if winner is None:
        return [0.0, 0.0]
    elif winner == 0:
        return [1.0, -1.0]
    else:
        return [-1.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    current_player = get_current_player(state)
    for rank in range(5):
        for file in range(5):
            piece = state['board'][rank][file]
            if piece != '.':
                # Pawn movement
                if piece == 'P':
                    if current_player == 0:
                        if rank == 1:
                            legal_actions.append(f"P_{chr(ord('a') + file)}_{chr(ord('a') + file + 1)}")
                        elif rank == 2:
                            legal_actions.append(f"P_{chr(ord('a') + file)}_{chr(ord('a') + file + 1)}")
                            legal_actions.append(f"P_{chr(ord('a') + file)}_{chr(ord('a') + file + 2)}")
                    else:
                        if rank == 4:
                            legal_actions.append(f"P_{chr(ord('e') - file)}_{chr(ord('e') - file - 1)}")
                        elif rank == 3:
                            legal_actions.append(f"P_{chr(ord('e') - file)}_{chr(ord('e') - file - 1)}")
                            legal_actions.append(f"P_{chr(ord('e') - file)}_{chr(ord('e') - file - 2)}")
                # Other pieces
                if piece in ('R', 'N', 'B', 'Q'):
                    for move in [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]:
                        next_rank, next_file = rank + move[1], file + move[0]
                        if 0 <= next_rank < 5 and 0 <= next_file < 5 and state['board'][next_rank][next_file] == '.':
                            legal_actions.append(f"{piece}_{chr(ord('a') + file)}_{chr(ord('a') + next_file)}")
                        elif 0 <= next_rank < 5 and 0 <= next_file < 5 and state['board'][next_rank][next_file] != '.':
                            legal_actions.append(f"{piece}_{chr(ord('a') + file)}_{chr(ord('a') + next_file)}_{state['board'][next_rank][next_file]}")
                # Castling
                if piece == 'R' and state['board'][rank][file] == 'R':
                    if current_player == 0 and rank == 0 and file in (0, 7):
                        if state['board'][1][file] == '.' and state['board'][2][file] == '.':
                            legal_actions.append("R_a1_a3")
                        if state['board'][3][file] == '.' and state['board'][4][file] == '.':
                            legal_actions.append("R_a1_a5")
                    elif current_player == 1 and rank == 4 and file in (0, 7):
                        if state['board'][3][file] == '.' and state['board'][2][file] == '.':
                            legal_actions.append("R_e1_e3")
                        if state['board'][1][file] == '.' and state['board'][0][file] == '.':
                            legal_actions.append("R_e1_e5")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {
        'board': state['board'],
        'turn': get_current_player(state),
        'winner': state['winner']
    }
    player_1_obs = {
        'board': state['board'],
        'turn': get_current_player(state),
        'winner': state['winner']
    }
    return [player_0_obs, player_1_obs]