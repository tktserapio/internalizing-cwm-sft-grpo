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
        'current_player': 0,
        'turn_count': 0,
        'winner': None
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    def update_board(board: Dict[str, Any], action: Action) -> Dict[str, Any]:
        """
        Update the board based on the given action.
        """
        piece, from_square, to_square = action.split('_')
        from_square = f"{from_square[0]}{from_square[1]}"
        to_square = f"{to_square[0]}{to_square[1]}"
        
        # Capture logic
        if piece == 'P' and abs(ord(from_square[0]) - ord(to_square[0])) == 1 and from_square[1] != to_square[1]:
            captured_piece = board[from_square]
            del board[from_square]
            board[to_square] = captured_piece
        
        # Promotion logic
        if piece == 'P' and (to_square[1] == '1' or to_square[1] == '5'):
            promoted_piece = input("Enter the promoted piece (Q/R/B/N): ").upper()
            board[to_square] = promoted_piece
        
        # Move logic
        board[to_square] = board.pop(from_square)
        
        return board
    
    def promote_pawn(board: Dict[str, Any], to_square: str) -> None:
        """
        Handle pawn promotion.
        """
        promoted_piece = input("Enter the promoted piece (Q/R/B/N): ").upper()
        board[to_square] = promoted_piece
    
    def castling(board: Dict[str, Any], from_square: str, to_square: str) -> None:
        """
        Handle castling logic (not implemented).
        """
        pass
    
    def en_passant(board: Dict[str, Any], from_square: str, to_square: str) -> None:
        """
        Handle en passant capture.
        """
        pass
    
    def check_promotion(board: Dict[str, Any], to_square: str) -> bool:
        """
        Check if the move results in a pawn promotion.
        """
        return board[to_square] == 'P' and (to_square[1] == '1' or to_square[1] == '5')
    
    def check_castle(board: Dict[str, Any], from_square: str, to_square: str) -> bool:
        """
        Check if the move involves castling.
        """
        return False
    
    def check_en_passant(board: Dict[str, Any], from_square: str, to_square: str) -> bool:
        """
        Check if the move involves en passant.
        """
        return False
    
    def check_check(board: Dict[str, Any], to_square: str, piece: str) -> bool:
        """
        Check if the move puts the king in check.
        """
        king_square = 'e1' if board['current_player'] == 0 else 'e5'
        if piece == 'K':
            return True
        return False
    
    def check_checkmate(board: Dict[str, Any], to_square: str, piece: str) -> bool:
        """
        Check if the move results in checkmate.
        """
        return False
    
    def check_stalemate(board: Dict[str, Any]) -> bool:
        """
        Check if the move results in a stalemate.
        """
        return False
    
    def check_draw(board: Dict[str, Any]) -> bool:
        """
        Check if the move results in a draw.
        """
        return False
    
    # Apply the action
    updated_board = update_board(state['board'], action)
    state['board'] = updated_board
    
    # Determine the winner
    if check_checkmate(updated_board, to_square, piece):
        state['winner'] = board['current_player']
    
    # Increment the turn count
    state['turn_count'] += 1
    state['current_player'] = 1 - state['current_player']
    
    return state

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
    if state['winner'] is not None:
        return [-1.0, 1.0] if state['winner'] == 0 else [1.0, -1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    # Implementing the logic to generate legal actions would require a more complex algorithm
    # This is a placeholder function
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    # Placeholder for observations
    return [{'board': state['board'], 'current_player': state['current_player']} for _ in range(2)]