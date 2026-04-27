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
    
    # Parse the action
    piece, from_square, to_square = action.split('_')
    from_row, from_col = ord(from_square[0]) - ord('a'), int(from_square[1]) - 1
    to_row, to_col = ord(to_square[0]) - ord('a'), int(to_square[1]) - 1
    
    # Get the piece at the from_square
    piece_at_from = new_state['board'][from_row][from_col]
    
    # Update the board
    new_state['board'][from_row][from_col] = '.'
    new_state['board'][to_row][to_col] = piece_at_from
    
    # Handle pawn promotion
    if piece == 'P' and (to_row == 0 or to_row == 4):
        new_state['board'][to_row][to_col] = f'{piece}_e{to_col + 1}'
    
    # Handle castling
    # Castling is not implemented in this 5x5 variant
    
    # Handle en passant
    # En passant is not implemented in this 5x5 variant
    
    # Handle promotion
    if piece == 'P' and (to_row == 0 or to_row == 4):
        new_state['board'][to_row][to_col] = f'{piece}_e{to_col + 1}'
    
    # Determine the winner
    if is_checkmate(new_state):
        new_state['winner'] = 1 if new_state['turn'] == 0 else 0
        new_state['turn'] = -4  # Terminal state
    
    return new_state

def is_checkmate(state: State) -> bool:
    """
    Determines if the current state is a checkmate.
    """
    king_row, king_col = find_king_position(state)
    king_pos = f'{chr(king_row + ord("a"))}{king_col + 1}'
    
    # Check if there are any legal moves for the opponent
    opponent_moves = get_legal_actions(state)
    if not opponent_moves:
        return True
    
    # Check if the opponent can put the king in check
    for move in opponent_moves:
        new_state = apply_action(state.copy(), move)
        if is_in_check(new_state, 1 - state['turn']):
            return False
    
    return True

def find_king_position(state: State) -> tuple[int, int]:
    """
    Finds the position of the king in the given state.
    """
    for row in range(5):
        for col in range(5):
            if state['board'][row][col] == 'k':
                return row, col
            elif state['board'][row][col] == 'K':
                return row, col
    
    raise ValueError("No king found in the state")

def is_in_check(state: State, player_id: int) -> bool:
    """
    Determines if the player in the given state is in check.
    """
    king_row, king_col = find_king_position(state)
    king_pos = f'{chr(king_row + ord("a"))}{king_col + 1}'
    
    # Get the opponent's pieces
    opponent_pieces = [piece for row in state['board'] for piece in row if piece != '.']
    
    # Check if any of the opponent's pieces can put the king in check
    for piece in opponent_pieces:
        if piece in ['N', 'B', 'Q']:
            if is_in_check_by_piece(state, piece, king_row, king_col):
                return True
        elif piece == 'P':
            if piece_is_promoted(state, king_row, king_col):
                if is_in_check_by_piece(state, 'Q', king_row, king_col):
                    return True
                elif is_in_check_by_piece(state, 'R', king_row, king_col):
                    return True
                elif is_in_check_by_piece(state, 'B', king_row, king_col):
                    return True
                elif is_in_check_by_piece(state, 'N', king_row, king_col):
                    return True
            else:
                if is_in_check_by_piece(state, 'P', king_row, king_col):
                    return True
        elif piece == 'R':
            if is_in_check_by_piece(state, 'Q', king_row, king_col):
                return True
            elif is_in_check_by_piece(state, 'B', king_row, king_col):
                return True
            elif is_in_check_by_piece(state, 'N', king_row, king_col):
                return True
        elif piece == 'B':
            if is_in_check_by_piece(state, 'Q', king_row, king_col):
                return True
            elif is_in_check_by_piece(state, 'R', king_row, king_col):
                return True
            elif is_in_check_by_piece(state, 'N', king_row, king_col):
                return True
        elif piece == 'N':
            if is_in_check_by_piece(state, 'Q', king_row, king_col):
                return True
            elif is_in_check_by_piece(state, 'R', king_row, king_col):
                return True
            elif is_in_check_by_piece(state, 'B', king_row, king_col):
                return True
        elif piece == 'Q':
            if is_in_check_by_piece(state, 'Q', king_row, king_col):
                return True
            elif is_in_check_by_piece(state, 'R', king_row, king_col):
                return True
            elif is_in_check_by_piece(state, 'B', king_row, king_col):
                return True
            elif is_in_check_by_piece(state, 'N', king_row, king_col):
                return True
    
    return False

def is_in_check_by_piece(state: State, piece: str, king_row: int, king_col: int) -> bool:
    """
    Determines if the given piece can put the king in check.
    """
    for row in range(5):
        for col in range(5):
            if state['board'][row][col] == '.':
                continue
            
            if piece == 'N':
                if is_knight_attacks_king(state, row, col, king_row, king_col):
                    return True
            elif piece == 'B':
                if is_bishop_attacks_king(state, row, col, king_row, king_col):
                    return True
            elif piece == 'R':
                if is_rook_attacks_king(state, row, col, king_row, king_col):
                    return True
            elif piece == 'Q':
                if is_queen_attacks_king(state, row, col, king_row, king_col):
                    return True
            elif piece == 'P':
                if piece_is_promoted(state, row, col):
                    if is_pawn_attacks_king(state, row, col, king_row, king_col):
                        return True
                else:
                    if is_pawn_attacks_king(state, row, col, king_row, king_col):
                        return True
    
    return False

def is_knight_attacks_king(state: State, row: int, col: int, king_row: int, king_col: int) -> bool:
    """
    Checks if a knight can attack the king.
    """
    possible_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    for move in possible_moves:
        new_row, new_col = row + move[0], col + move[1]
        if 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] == 'k':
            return True
    
    return False

def is_bishop_attacks_king(state: State, row: int, col: int, king_row: int, king_col: int) -> bool:
    """
    Checks if a bishop can attack the king.
    """
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    for direction in directions:
        new_row, new_col = row + direction[0], col + direction[1]
        while 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] != '.':
            if state['board'][new_row][new_col] == 'k':
                return True
            new_row += direction[0]
            new_col += direction[1]
    
    return False

def is_rook_attacks_king(state: State, row: int, col: int, king_row: int, king_col: int) -> bool:
    """
    Checks if a rook can attack the king.
    """
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for direction in directions:
        new_row, new_col = row + direction[0], col + direction[1]
        while 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] != '.':
            if state['board'][new_row][new_col] == 'k':
                return True
            new_row += direction[0]
            new_col += direction[1]
    
    return False

def is_queen_attacks_king(state: State, row: int, col: int, king_row: int, king_col: int) -> bool:
    """
    Checks if a queen can attack the king.
    """
    return is_bishop_attacks_king(state, row, col, king_row, king_col) or is_rook_attacks_king(state, row, col, king_row, king_col)

def is_pawn_attacks_king(state: State, row: int, col: int, king_row: int, king_col: int) -> bool:
    """
    Checks if a pawn can attack the king.
    """
    if state['board'][row][col] == 'P':
        if row == 1 and king_row == 0:
            return True
        elif row == 4 and king_row == 5:
            return True
        else:
            return False
    else:
        return False

def piece_is_promoted(state: State, row: int, col: int) -> bool:
    """
    Determines if the piece at the given position is a promoted pawn.
    """
    return state['board'][row][col] in ['P', 'P']

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
    return [1.0 if state['winner'] == 0 else -1.0, 1.0 if state['winner'] == 1 else -1.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    for row in range(5):
        for col in range(5):
            if state['board'][row][col] != '.':
                piece = state['board'][row][col]
                
                # Pawn moves
                if piece == 'P':
                    if row == 1:
                        legal_actions.append(f"P_{chr(row + ord('a'))}_{chr(col + 1)}")
                    if row == 4:
                        legal_actions.append(f"P_{chr(row + ord('a'))}_{chr(col + 1)}")
                    if state['board'][row + 1][col] == '.':
                        legal_actions.append(f"P_{chr(row + ord('a'))}_{chr(col + 1)}")
                    if state['board'][row + 1][col] != '.' and state['board'][row + 1][col][0] == 'P':
                        legal_actions.append(f"P_{chr(row + ord('a'))}_{chr(col + 1)}_Q")
                    if state['board'][row + 1][col] != '.' and state['board'][row + 1][col][0] == 'P' and state['board'][row + 2][col] == '.':
                        legal_actions.append(f"P_{chr(row + ord('a'))}_{chr(col + 1)}_P")
                elif piece == 'P' and state['board'][row + 1][col] != '.' and state['board'][row + 1][col][0] == 'P':
                    legal_actions.append(f"P_{chr(row + ord('a'))}_{chr(col + 1)}_P")
                
                # Knight moves
                if piece == 'N':
                    for move in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
                        new_row, new_col = row + move[0], col + move[1]
                        if 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] != '.':
                            legal_actions.append(f"N_{chr(row + ord('a'))}_{chr(col + 1)}_{chr(new_row + ord('a'))}_{chr(new_col + 1)}")
                
                # Bishop moves
                if piece == 'B':
                    for direction in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                        new_row, new_col = row + direction[0], col + direction[1]
                        while 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] != '.':
                            if state['board'][new_row][new_col] == 'k':
                                legal_actions.append(f"B_{chr(row + ord('a'))}_{chr(col + 1)}_{chr(new_row + ord('a'))}_{chr(new_col + 1)}")
                            new_row += direction[0]
                            new_col += direction[1]
                
                # Rook moves
                if piece == 'R':
                    for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        new_row, new_col = row + direction[0], col + direction[1]
                        while 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] != '.':
                            if state['board'][new_row][new_col] == 'k':
                                legal_actions.append(f"R_{chr(row + ord('a'))}_{chr(col + 1)}_{chr(new_row + ord('a'))}_{chr(new_col + 1)}")
                            new_row += direction[0]
                            new_col += direction[1]
                
                # Queen moves
                if piece == 'Q':
                    for direction in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                        new_row, new_col = row + direction[0], col + direction[1]
                        while 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] != '.':
                            if state['board'][new_row][new_col] == 'k':
                                legal_actions.append(f"Q_{chr(row + ord('a'))}_{chr(col + 1)}_{chr(new_row + ord('a'))}_{chr(new_col + 1)}")
                            new_row += direction[0]
                            new_col += direction[1]
                
                # King moves
                if piece == 'K':
                    for move in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                        new_row, new_col = row + move[0], col + move[1]
                        if 0 <= new_row < 5 and 0 <= new_col < 5 and state['board'][new_row][new_col] == '.':
                            legal_actions.append(f"K_{chr(row + ord('a'))}_{chr(col + 1)}_{chr(new_row + ord('a'))}_{chr(new_col + 1)}")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {
        'board': state['board'],
        'turn': state['turn'],
        'winner': state['winner']
    }
    player_1_obs = {
        'board': state['board'],
        'turn': state['turn'],
        'winner': state['winner']
    }
    return [player_0_obs, player_1_obs]