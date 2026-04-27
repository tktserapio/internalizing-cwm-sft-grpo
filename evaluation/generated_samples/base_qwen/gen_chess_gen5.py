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

# Helper functions
def convert_position(position):
    """Converts file and rank to algebraic notation for the 5x5 board."""
    file, rank = position
    return f"{chr(ord('a') + file)}{5 - rank}"

def convert_algebraic_to_position(algebraic):
    """Converts algebraic notation back to file and rank for the 5x5 board."""
    file, rank = algebraic[0], 5 - int(algebraic[1])
    return (ord(file) - ord('a'), rank)

def is_valid_move(action, state):
    """Checks if the given action is valid in the current state."""
    piece, from_pos, to_pos = action.split('_')
    from_pos, to_pos = convert_position(from_pos), convert_position(to_pos)
    
    # Check if the piece exists at the from position
    if from_pos not in state or state[from_pos]['piece'] != piece:
        return False
    
    # Check if the to position is empty
    if state[to_pos]['piece']:
        return False
    
    # Check if the move is within the bounds of the board
    if not (0 <= int(from_pos[0]) < 5 and 0 <= int(from_pos[1]) < 5) or not (0 <= int(to_pos[0]) < 5 and 0 <= int(to_pos[1]) < 5):
        return False
    
    return True

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    initial_state = {
        'a1': {'piece': 'R', 'color': 'Black'},
        'b1': {'piece': 'N', 'color': 'Black'},
        'c1': {'piece': 'B', 'color': 'Black'},
        'd1': {'piece': 'Q', 'color': 'Black'},
        'e1': {'piece': 'K', 'color': 'Black'},
        'a2': {'piece': 'P', 'color': 'Black'},
        'b2': {'piece': 'P', 'color': 'Black'},
        'c2': {'piece': 'P', 'color': 'Black'},
        'd2': {'piece': 'P', 'color': 'Black'},
        'e2': {'piece': 'P', 'color': 'Black'},
        'a3': {'piece': '.', 'color': None},
        'b3': {'piece': '.', 'color': None},
        'c3': {'piece': '.', 'color': None},
        'd3': {'piece': '.', 'color': None},
        'e3': {'piece': '.', 'color': None},
        'a4': {'piece': '.', 'color': None},
        'b4': {'piece': '.', 'color': None},
        'c4': {'piece': '.', 'color': None},
        'd4': {'piece': '.', 'color': None},
        'e4': {'piece': '.', 'color': None},
        'a5': {'piece': 'R', 'color': 'White'},
        'b5': {'piece': 'N', 'color': 'White'},
        'c5': {'piece': 'B', 'color': 'White'},
        'd5': {'piece': 'Q', 'color': 'White'},
        'e5': {'piece': 'K', 'color': 'White'},
        'a6': {'piece': 'P', 'color': 'White'},
        'b6': {'piece': 'P', 'color': 'White'},
        'c6': {'piece': 'P', 'color': 'White'},
        'd6': {'piece': 'P', 'color': 'White'},
        'e6': {'piece': 'P', 'color': 'White'},
        'a7': {'piece': '.', 'color': None},
        'b7': {'piece': '.', 'color': None},
        'c7': {'piece': '.', 'color': None},
        'd7': {'piece': '.', 'color': None},
        'e7': {'piece': '.', 'color': None},
        'a8': {'piece': '.', 'color': None},
        'b8': {'piece': '.', 'color': None},
        'c8': {'piece': '.', 'color': None},
        'd8': {'piece': '.', 'color': None},
        'e8': {'piece': '.', 'color': None}
    }
    return initial_state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy.deepcopy(state)
    piece, from_pos, to_pos = action.split('_')
    from_pos, to_pos = convert_position(from_pos), convert_position(to_pos)
    
    # Move the piece
    new_state[to_pos]['piece'] = new_state[from_pos]['piece']
    new_state[to_pos]['color'] = new_state[from_pos]['color']
    new_state[from_pos]['piece'], new_state[from_pos]['color'] = '.', None
    
    # Handle special cases like pawn promotion
    if new_state[to_pos]['piece'] == 'P' and (int(to_pos[1]) == 0 or int(to_pos[1]) == 5):
        new_state[to_pos]['piece'] = 'Q'
    
    # Handle castling
    # Castling is not implemented in this 5x5 variant
    
    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    for pos, data in state.items():
        if data['piece'] == 'K':
            if data['color'] == 'Black':
                return 1
            else:
                return 0

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return ['Black', 'White'][player_id]

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    # In a real game, you would calculate the rewards based on the game state.
    # For now, we assume a simple scoring system where the winner gets +1.0 and the loser gets -1.0.
    if state['e1']['piece'] == '.':
        return [1.0, -1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    for pos, data in state.items():
        if data['piece']:
            piece = data['piece']
            color = data['color']
            from_pos = pos
            
            # Pawn movement
            if piece == 'P':
                if color == 'Black':
                    if state[f'{pos[0]}{int(pos[1]) + 1}']['piece'] == '.':
                        legal_actions.append(f"P_{pos}_{f'{pos[0]}{int(pos[1]) + 1}'}")
                    if state[f'{pos[0]}{int(pos[1]) + 2}']['piece'] == '.' and state[f'{pos[0]}{int(pos[1]) + 1}']['piece'] == '.':
                        legal_actions.append(f"P_{pos}_{f'{pos[0]}{int(pos[1]) + 2}'}")
                    if state[f'{pos[0]}{int(pos[1]) + 1}']['piece'] and state[f'{pos[0]}{int(pos[1]) + 1}']['piece'][0] == 'P':
                        legal_actions.append(f"P_{pos}_{f'{pos[0]}{int(pos[1]) + 1}_Q"}  # This is incorrect, should be promotion logic
                elif color == 'White':
                    if state[f'{pos[0]}{int(pos[1]) - 1}']['piece'] == '.':
                        legal_actions.append(f"P_{pos}_{f'{pos[0]}{int(pos[1]) - 1}'}")
                    if state[f'{pos[0]}{int(pos[1]) - 2}']['piece'] == '.' and state[f'{pos[0]}{int(pos[1]) - 1}']['piece'] == '.':
                        legal_actions.append(f"P_{pos}_{f'{pos[0]}{int(pos[1]) - 2}'}")
                    if state[f'{pos[0]}{int(pos[1]) - 1}']['piece'] and state[f'{pos[0]}{int(pos[1]) - 1}']['piece'][0] == 'P':
                        legal_actions.append(f"P_{pos}_{f'{pos[0]}{int(pos[1]) - 1}_Q"}  # This is incorrect, should be promotion logic
                
            # Other pieces
            if piece in ['R', 'N', 'B', 'Q', 'K']:
                for to_pos in [(int(pos[0]) + 1, int(pos[1])), (int(pos[0]) - 1, int(pos[1])), (int(pos[0]), int(pos[1]) + 1), (int(pos[0]), int(pos[1]) - 1)]:
                    if 0 <= int(to_pos[0]) < 5 and 0 <= int(to_pos[1]) < 5 and state[f'{to_pos[0]}{to_pos[1]}']['piece'] == '.':
                        legal_actions.append(f"{piece}_{pos}_{f'{to_pos[0]}{to_pos[1]}'}")
                    elif 0 <= int(to_pos[0]) < 5 and 0 <= int(to_pos[1]) < 5 and state[f'{to_pos[0]}{to_pos[1]}']['piece'] and state[f'{to_pos[0]}{to_pos[1]}']['color'] != color:
                        legal_actions.append(f"{piece}_{pos}_{f'{to_pos[0]}{to_pos[1]}'}")
                
                # Special moves like castling
                # Castling is not implemented in this 5x5 variant
                
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {}
    player_1_obs = {}
    
    for pos, data in state.items():
        if data['piece']:
            piece = data['piece']
            color = data['color']
            
            if color == 'Black':
                player_1_obs[pos] = {'piece': piece}
            else:
                player_0_obs[pos] = {'piece': piece}
    
    return [player_0_obs, player_1_obs]