import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import numpy as np

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper functions
def parse_action(action_str: Action) -> tuple[int, int]:
    """Parses the action string into a (row, col) tuple."""
    row_col_str = action_str.split(',')
    return (int(row_col_str[0]), int(row_col_str[1]))

def is_valid_action(state: State, action: Action) -> bool:
    """Checks if the given action is valid in the current state."""
    row, col = parse_action(action)
    return 0 <= row < 6 and 0 <= col < 6 and state['board'][row][col] == '_'

def apply_action(state: State, action: Action) -> State:
    """Applies an action to the state and returns the new state."""
    new_state = state.copy()
    row, col = parse_action(action)
    new_state['board'][row][col] = new_state['current_player']
    new_state['current_player'] = 1 - new_state['current_player']
    return new_state

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    board = np.full((6, 6), '_')
    return {
        'board': board,
        'current_player': 0,
        'winner': None
    }

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Player {}'.format(player_id + 1)

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['winner'] is not None:
        return [-1.0, 1.0] if state['winner'] == 0 else [1.0, -1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    for row in range(6):
        for col in range(6):
            if state['board'][row][col] == '_':
                legal_actions.append(f"{row},{col}")
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    for player_id in range(2):
        observation = {'board': state['board'].copy(), 'legal_actions': get_legal_actions(state)}
        observation['board'][state['current_player']] = 'X'
        observation['board'][1 - state['current_player']] = 'O'
        observations.append(observation)
    return observations

# Main game logic
def main():
    state = get_initial_state()
    while True:
        print("Current State:")
        print(state['board'])
        print("Legal Actions:", get_legal_actions(state))
        action = input("Enter your action (e.g., 0,0): ")
        if not is_valid_action(state, action):
            print("Invalid action! Try again.")
            continue
        state = apply_action(state, action)
        if get_current_player(state) == -4:
            print("Game Over!")
            print("Winner:", get_player_name(get_current_player(state)))
            break
        print("Opponent's Turn...")
        # Simulate opponent's move (for demonstration purposes)
        state = apply_action(state, get_legal_actions(state)[0])
        if get_current_player(state) == -4:
            print("Game Over!")
            print("Winner:", get_player_name(get_current_player(state)))
            break

if __name__ == "__main__":
    main()