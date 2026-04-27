import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initialize the state with the initial board setup
    initial_board = {
        'r': (1, 1), 'n': (1, 2), 'b': (1, 3), 'q': (1, 4), 'k': (1, 5),
        'p': [(2, i) for i in range(5)],
        'R': (5, 1), 'N': (5, 2), 'B': (5, 3), 'Q': (5, 4), 'K': (5, 5),
        'p': [(4, i) for i in range(5)]
    }
    state = {'board': initial_board, 'turn': 0, 'winner': None}
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = copy.deepcopy(state)
    rank_from, file_from, rank_to, file_to = parse_coordinates(action.split('_')[1:])
    piece = get_piece_at(new_state, rank_from, file_from)
    
    if piece == 'K':
        # Check for checkmate
        if not get_legal_actions(new_state):
            return new_state
    
    if is_valid_move(action, new_state):
        new_state['board'][convert_coordinates(rank_to, file_to)] = piece
        new_state['board'][convert_coordinates(rank_from, file_from)] = '.'
        new_state['turn'] = (new_state['turn'] + 1) % 2
        new_state['winner'] = get_winner(new_state)
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['turn']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    winner = state['winner']
    if winner is None:
        return [0.0, 0.0]
    elif winner == 0:
        return [1.0, -1.0]
    else:
        return [-1.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    current_color = 'W' if state['turn'] == 0 else 'B'
    for rank_from, files_from in state['board'].items():
        if files_from != '.':
            for file_from in files_from:
                rank_from, file_from = parse_coordinates(file_from)
                for rank_to, file_to in state['board'].items():
                    if file_to != '.':
                        for file_to in file_to:
                            rank_to, file_to = parse_coordinates(file_to)
                            if is_valid_move(f'{rank_from}_{file_from}_{rank_to}_{file_to}', state):
                                legal_actions.append(f'{rank_from}_{file_from}_{rank_to}_{file_to}')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {}
    player_1_obs = {}
    for rank, files in state['board'].items():
        for file, piece in files.items():
            rank, file = parse_coordinates(file)
            if piece == 'K':
                player_0_obs[convert_coordinates(rank, file)] = 'K'
                player_1_obs[convert_coordinates(rank, file)] = 'K'
            else:
                player_0_obs[convert_coordinates(rank, file)] = piece
                player_1_obs[convert_coordinates(rank, file)] = piece
    return [player_0_obs, player_1_obs]

def get_winner(state: State) -> int:
    """Determines the winner of the game."""
    # Implement logic to determine the winner
    pass