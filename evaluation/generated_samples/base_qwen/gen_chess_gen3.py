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

# Helper function to create a new state based on the given action
def apply_action_helper(state: State, action: Action) -> State:
    """
    Apply an action to the current state and return the new state.
    This function is used internally to avoid mutating the original state.
    """
    new_state = copy.deepcopy(state)
    piece, from_square, to_square = action.split('_')
    # Update the piece location
    new_state[from_square] = '.'
    new_state[to_square] = piece
    # Handle promotions
    if piece == 'P' and to_square != 'e5':
        new_state[to_square] = piece + '_Q'  # Promotion to Queen
    elif piece == 'P' and to_square != 'e4':
        new_state[to_square] = piece + '_R'  # Promotion to Rook
    elif piece == 'P' and to_square != 'e3':
        new_state[to_square] = piece + '_B'  # Promotion to Bishop
    elif piece == 'P' and to_square != 'e2':
        new_state[to_square] = piece + '_N'  # Promotion to Knight
    return new_state

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    initial_board = {
        'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K',
        'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P',
        'a3': '.', 'b3': '.', 'c3': '.', 'd3': '.', 'e3': '.',
        'a4': '.', 'b4': '.', 'c4': '.', 'd4': '.', 'e4': '.',
        'a5': 'r', 'b5': 'n', 'c5': 'b', 'd5': 'q', 'e5': 'k'
    }
    return initial_board

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    return apply_action_helper(state, action)

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    # Determine the current player based on whose turn it is
    if state['a1'] == 'r' and state['b1'] == 'n' and state['c1'] == 'b' and state['d1'] == 'q' and state['e1'] == 'k':
        return 1  # Black's turn
    elif state['a5'] == 'r' and state['b5'] == 'n' and state['c5'] == 'b' and state['d5'] == 'q' and state['e5'] == 'k':
        return 0  # White's turn
    else:
        return -4  # Terminal state

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    if player_id == 0:
        return "White"
    elif player_id == 1:
        return "Black"
    else:
        return "Unknown"

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards.
    """
    # Determine the winner based on the current state
    if state['a1'] == 'r' and state['b1'] == 'n' and state['c1'] == 'b' and state['d1'] == 'q' and state['e1'] == 'k':
        return [-1.0, 1.0]  # Black loses, White wins
    elif state['a5'] == 'r' and state['b5'] == 'n' and state['c5'] == 'b' and state['d5'] == 'q' and state['e5'] == 'k':
        return [1.0, -1.0]  # White loses, Black wins
    else:
        return [0.0, 0.0]  # No winner yet

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    for square, piece in state.items():
        if piece != '.':
            # Pawn movement
            if piece == 'P':
                if state[square[0] + '3'] == '.' and state[square[0] + '4'] == '.':
                    legal_actions.append(f"P_{square}_{square}_Q")  # Promotion to Queen
                    legal_actions.append(f"P_{square}_{square}_R")  # Promotion to Rook
                    legal_actions.append(f"P_{square}_{square}_B")  # Promotion to Bishop
                    legal_actions.append(f"P_{square}_{square}_N")  # Promotion to Knight
                elif state[square[0] + '3'] == '.':
                    legal_actions.append(f"P_{square}_{square + '2'}")
                elif state[square[0] + '4'] == '.':
                    legal_actions.append(f"P_{square}_{square + '3'}")
                else:
                    if state[square[0] + '3'] == '.':
                        legal_actions.append(f"P_{square}_{square + '2'}")
                    elif state[square[0] + '4'] == '.':
                        legal_actions.append(f"P_{square}_{square + '3'}")
            # Knight movement
            elif piece == 'N':
                legal_actions.append(f"N_{square}_a{chr(ord(square[0]) + 1) + square[1]}")
                legal_actions.append(f"N_{square}_a{chr(ord(square[0]) - 1) + square[1]}")
                legal_actions.append(f"N_{square}_b{chr(ord(square[0]) + 2) + square[1]}")
                legal_actions.append(f"N_{square}_b{chr(ord(square[0]) - 2) + square[1]}")
                legal_actions.append(f"N_{square}_c{chr(ord(square[0]) + 1) + square[1]}")
                legal_actions.append(f"N_{square}_c{chr(ord(square[0]) - 1) + square[1]}")
                legal_actions.append(f"N_{square}_d{chr(ord(square[0]) + 1) + square[1]}")
                legal_actions.append(f"N_{square}_d{chr(ord(square[0]) - 1) + square[1]}")
            # Bishop movement
            elif piece == 'B':
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]) + i)}{square[1]}"] == '.':
                        legal_actions.append(f"B_{square}_{chr(ord(square[0]) + i)}{square[1]}")
                    else:
                        break
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]) - i)}{square[1]}"] == '.':
                        legal_actions.append(f"B_{square}_{chr(ord(square[0]) - i)}{square[1]}")
                    else:
                        break
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1] + i}"] == '.':
                        legal_actions.append(f"B_{square}_{chr(ord(square[0]))}{square[1] + i}")
                    else:
                        break
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1] - i}"] == '.':
                        legal_actions.append(f"B_{square}_{chr(ord(square[0]))}{square[1] - i}")
                    else:
                        break
            # Rook movement
            elif piece == 'R':
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1]}"] == '.':
                        legal_actions.append(f"R_{square}_{chr(ord(square[0]))}{square[1]}")
                    else:
                        break
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1]}"] == '.':
                        legal_actions.append(f"R_{square}_{chr(ord(square[0]))}{square[1]}")
                    else:
                        break
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1]}" + i] == '.':
                        legal_actions.append(f"R_{square}_{chr(ord(square[0]))}{square[1]}" + i)
                    else:
                        break
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1]}" + i] == '.':
                        legal_actions.append(f"R_{square}_{chr(ord(square[0]))}{square[1]}" + i)
                    else:
                        break
            # Queen movement
            elif piece == 'Q':
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1]}"] == '.':
                        legal_actions.append(f"Q_{square}_{chr(ord(square[0]))}{square[1]}")
                    else:
                        break
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1]}" + i] == '.':
                        legal_actions.append(f"Q_{square}_{chr(ord(square[0]))}{square[1]}" + i)
                    else:
                        break
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1]}" + i] == '.':
                        legal_actions.append(f"Q_{square}_{chr(ord(square[0]))}{square[1]}" + i)
                    else:
                        break
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1]}" + i] == '.':
                        legal_actions.append(f"Q_{square}_{chr(ord(square[0]))}{square[1]}" + i)
                    else:
                        break
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1]}" + i] == '.':
                        legal_actions.append(f"Q_{square}_{chr(ord(square[0]))}{square[1]}" + i)
                    else:
                        break
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1]}" + i] == '.':
                        legal_actions.append(f"Q_{square}_{chr(ord(square[0]))}{square[1]}" + i)
                    else:
                        break
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1]}" + i] == '.':
                        legal_actions.append(f"Q_{square}_{chr(ord(square[0]))}{square[1]}" + i)
                    else:
                        break
                for i in range(1, 5):
                    if state[f"{chr(ord(square[0]))}{square[1]}" + i] == '.':
                        legal_actions.append(f"Q_{square}_{chr(ord(square[0]))}{square[1]}" + i)
                    else:
                        break
            # King movement
            elif piece == 'K':
                if state['a1'] == '.':
                    legal_actions.append(f"K_{square}_a{chr(ord(square[0]) + 1) + square[1]}")
                if state['b1'] == '.':
                    legal_actions.append(f"K_{square}_a{chr(ord(square[0])) + square[1]}")
                if state['c1'] == '.':
                    legal_actions.append(f"K_{square}_a{chr(ord(square[0]) - 1) + square[1]}")
                if state['d1'] == '.':
                    legal_actions.append(f"K_{square}_b{chr(ord(square[0])) + square[1]}")
                if state['e1'] == '.':
                    legal_actions.append(f"K_{square}_b{chr(ord(square[0])) - 1 + square[1]}")
                if state['a5'] == '.':
                    legal_actions.append(f"K_{square}_a{chr(ord(square[0]) + 1) + square[1]}")
                if state['b5'] == '.':
                    legal_actions.append(f"K_{square}_a{chr(ord(square[0])) + square[1]}")
                if state['c5'] == '.':
                    legal_actions.append(f"K_{square}_a{chr(ord(square[0]) - 1) + square[1]}")
                if state['d5'] == '.':
                    legal_actions.append(f"K_{square}_b{chr(ord(square[0])) + square[1]}")
                if state['e5'] == '.':
                    legal_actions.append(f"K_{square}_b{chr(ord(square[0])) - 1 + square[1]}")
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {}
    player_1_obs = {}
    for square, piece in state.items():
        if piece != '.':
            file = square[0]
            rank = square[1]
            if file == 'a':
                player_0_obs[(rank, file)] = piece
            elif file == 'e':
                player_1_obs[(rank, file)] = piece
    return [player_0_obs, player_1_obs]