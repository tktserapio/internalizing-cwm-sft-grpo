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
    """Returns the initial game state before any actions are taken."""
    return {
        'board': {
            'A1': None,
            'A2': None,
            'A3': None,
            'A4': None,
            'B1': None,
            'B2': None,
            'B3': None,
            'C1': None,
            'C2': None,
            'C3': None
        },
        'current_player': 0,  # Black starts
        'turn': 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    row, col = map(int, action.split(','))

    if state['current_player'] == 0:  # Black's turn
        new_state['board'][f'A{col + 1}'] = 'B'
        new_state['current_player'] = 1  # Switch to White
    else:  # White's turn
        new_state['board'][f'A{col + 1}'] = 'W'
        new_state['current_player'] = 0  # Switch back to Black

    new_state['turn'] += 1
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # In a real game, this would calculate the score based on the board state
    # Here we assume a simple win/loss scenario
    if check_win(state):
        return [1.0, -1.0]
    return [0.0, 0.0]

def check_win(state: State) -> bool:
    """Checks if a player has won the game."""
    board = state['board']
    corners = ['A1', 'A4', 'C1', 'C3']
    edges = [
        ('A1', 'A2'), ('A2', 'A3'), ('A3', 'A4'),
        ('A1', 'B1'), ('A2', 'B2'), ('A3', 'B3'),
        ('A4', 'C4'), ('C1', 'C2'), ('C2', 'C3')
    ]
    
    def is_connected(start: str, end: str) -> bool:
        visited = set()
        stack = [(start, 0)]
        
        while stack:
            node, depth = stack.pop()
            if node == end:
                return True
            if depth > 2:
                continue
            visited.add(node)
            for neighbor in board[node]:
                if neighbor not in visited:
                    stack.append((neighbor, depth + 1))
        
        return False
    
    for corner in corners:
        if board[corner] is None:
            continue
        for edge in edges:
            if board[edge[0]] is None or board[edge[1]] is None:
                continue
            if board[edge[0]] != board[edge[1]]:
                continue
            if is_connected(edge[0], corner) or is_connected(edge[1], corner):
                return True
    return False

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    legal_actions = []
    for cell in board:
        if board[cell] is None:
            legal_actions.append(cell)
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = []
    for player_id in range(2):
        observation = {}
        for cell, color in board.items():
            if color == 'B':
                observation[cell] = {'color': 'Black', 'position': cell}
            elif color == 'W':
                observation[cell] = {'color': 'White', 'position': cell}
        observations.append(observation)
    return observations