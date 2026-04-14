import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to convert coordinates to string format
def coord_to_string(row: int, col: int) -> Action:
    """Converts row and column coordinates to a string format used in the game."""
    return f"{col},{row}"

# Helper function to convert string format back to coordinates
def string_to_coord(action: Action) -> Tuple[int, int]:
    """Converts a string action to a tuple of coordinates."""
    parts = action.split(',')
    return (int(parts[0]), int(parts[1]))

# Initial state of the game
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Size-4 board
    board = {
        'A': {'1': None, '3': None, '6': None},
        'B': {'2': None, '5': None, '7': None, '8': None, '9': None},
        'C': {'4': None, '9': None}
    }
    return {
        'board': board,
        'current_player': 0,  # Black starts
        'turn': 0
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    current_player = state['current_player']
    board = state['board']
    turn = state['turn']
    
    # Convert action to coordinates
    row, col = string_to_coord(action)
    
    # Check if the cell is empty
    if board[str(current_player)][f'{col}'] is not None:
        raise ValueError(f"Cell {action} is already occupied.")
    
    # Place the stone
    board[str(current_player)][f'{col}'] = turn
    
    # Update the turn counter
    turn += 1
    
    # Determine the next player
    next_player = 1 if current_player == 0 else 0
    
    # Return the new state
    return {
        'board': board,
        'current_player': next_player,
        'turn': turn
    }

# Get the current player
def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

# Get rewards per player
def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    # In this simple implementation, we assume the game ends when a player wins
    # and the other loses. We return [1.0, -1.0] for a win/loss scenario.
    if is_winner(state):
        return [1.0, -1.0]
    else:
        return [0.0, 0.0]

# Check if a player has won
def is_winner(state: State) -> bool:
    """Check if the current player has formed a connected group touching all three sides."""
    board = state['board']
    current_player = state['current_player']
    
    # Define the sides
    sides = {
        'A': ['1', '3', '6'],
        'B': ['2', '5', '7', '8', '9'],
        'C': ['4', '9']
    }
    
    # Check each side for a connected group
    for side in sides.values():
        for cell in side:
            if board[str(current_player)].get(cell) is not None:
                # Check horizontally
                if cell in ['1', '3', '6']:
                    if board[str(current_player)].get('2') is not None and board[str(current_player)].get('5') is not None:
                        return True
                    if board[str(current_player)].get('4') is not None and board[str(current_player)].get('9') is not None:
                        return True
                elif cell in ['2', '5', '7', '8', '9']:
                    if board[str(current_player)].get('1') is not None and board[str(current_player)].get('3') is not None:
                        return True
                    if board[str(current_player)].get('4') is not None and board[str(current_player)].get('6') is not None:
                        return True
                    if board[str(current_player)].get('7') is not None and board[str(current_player)].get('8') is not None:
                        return True
                elif cell in ['4', '9']:
                    if board[str(current_player)].get('1') is not None and board[str(current_player)].get('3') is not None:
                        return True
                    if board[str(current_player)].get('2') is not None and board[str(current_player)].get('5') is not None:
                        return True
    return False

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    current_player = state['current_player']
    turn = state['turn']
    
    # Get all empty cells
    empty_cells = []
    for row in board[str(current_player)]:
        if board[str(current_player)][row] is None:
            empty_cells.append(coord_to_string(turn, int(row)))
    
    # If there are no empty cells, the game is over
    if not empty_cells:
        return []
    
    return empty_cells

# Get observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    current_player = state['current_player']
    
    # Player 0 sees the full board
    player_0_obs = {
        'board': board[str(current_player)],
        'legal_actions': get_legal_actions(state),
        'current_player': current_player
    }
    
    # Player 1 sees the full board
    player_1_obs = {
        'board': board[str(1 - current_player)],
        'legal_actions': get_legal_actions(state),
        'current_player': 1 - current_player
    }
    
    return [player_0_obs, player_1_obs]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    
    # Simulate a few turns
    for turn in range(10):
        print(f"\nTurn {turn + 1}")
        print("Current Player:", get_player_name(initial_state['current_player']))
        print("Legal Actions:", get_legal_actions(initial_state))
        
        # Apply a random legal action
        legal_actions = get_legal_actions(initial_state)
        action = legal_actions[0]  # Randomly choose an action
        print("Action:", action)
        
        new_state = apply_action(initial_state, action)
        print("New State:", new_state)
        
        # Get the current player
        current_player = get_current_player(new_state)
        print("Current Player:", get_player_name(current_player))
        
        # Get the observations
        observations = get_observations(new_state)
        print("Observations:", observations)
        
        initial_state = new_state