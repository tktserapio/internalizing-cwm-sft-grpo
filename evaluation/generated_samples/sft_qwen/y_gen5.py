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

# Helper function to check if a move connects all three sides
def is_winner(state: State, player: int) -> bool:
    # Extract the board from the state
    board = state['board']
    # Check if the player's stones form a connected group that touches all three sides
    for side in ['A', 'B', 'C']:
        for cell in board[side]:
            if not is_connected(board, cell, player):
                return False
    return True

# Helper function to check if a group of stones is connected
def is_connected(board: dict[str, set[int]], cell: int, player: int) -> bool:
    def dfs(cell: int, visited: set[int]) -> bool:
        if cell in visited:
            return False
        visited.add(cell)
        for neighbor in board[str(cell)]:
            if neighbor in visited:
                continue
            if not is_connected(board, neighbor, player):
                return False
        return True
    return dfs(cell, set())

# Helper function to get the neighbors of a cell
def get_neighbors(cell: int) -> set[int]:
    neighbors = set()
    if cell % 3 == 0:
        neighbors.add(cell - 3)
    if cell % 3 != 2:
        neighbors.add(cell + 1)
    if cell % 3 != 0:
        neighbors.add(cell - 1)
    return neighbors

# Initial state
def get_initial_state() -> State:
    return {
        'board': {
            'A': set([1, 3, 6]),
            'B': set([2, 5, 9]),
            'C': set([6, 7, 8, 9])
        },
        'turn': 0,
        'winner': None
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = copy.deepcopy(state)
    player = state['turn'] % 2
    cell = int(action)
    
    # Update the board with the new stone
    new_state['board'][str(cell)].add(cell)
    
    # Switch the turn
    new_state['turn'] += 1
    
    # Check if the move leads to a winner
    if is_winner(new_state, player):
        new_state['winner'] = player
    else:
        new_state['winner'] = None
    
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state['turn'] % 2

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 0 else 'White'

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    if state['winner'] is not None:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    if state['winner'] is not None:
        return []
    legal_actions = []
    for cell in range(1, 10):
        if str(cell) not in state['board']:
            legal_actions.append(str(cell))
    return legal_actions

# Get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    if state['winner'] is not None:
        return [{}, {}]
    return [{cell: 1 for cell in state['board']['A']}, {cell: 1 for cell in state['board']['B']}]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    
    # Simulate a few moves
    state = apply_action(initial_state, "4")
    print("After move 1 (Black):", state)
    
    state = apply_action(state, "1")
    print("After move 2 (White):", state)
    
    state = apply_action(state, "7")
    print("After move 3 (Black):", state)
    
    state = apply_action(state, "5")
    print("After move 4 (White):", state)
    
    state = apply_action(state, "3")
    print("After move 5 (Black):", state)
    
    state = apply_action(state, "8")
    print("After move 6 (White):", state)
    
    state = apply_action(state, "2")
    print("After move 7 (Black):", state)
    
    print("Final State:", state)