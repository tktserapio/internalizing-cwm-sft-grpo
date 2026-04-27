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

# Helper function to check if a given position is within the board boundaries
def is_within_bounds(pos):
    return 0 <= pos[0] <= 4 and 0 <= pos[1] <= 4

# Initial state setup
def get_initial_state() -> State:
    # Player 0 (Blue) starts with units at (0, 0) and (0, 4)
    blue_units = [(0, 0), (0, 4)]
    # Player 1 (Red) starts with units at (4, 0) and (4, 4)
    red_units = [(4, 0), (4, 4)]
    return {
        'blue_units': blue_units,
        'red_units': red_units,
        'current_player': 0,
        'turn_count': 0,
        'center_square_occupied': False
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = copy.deepcopy(state)
    if action == 'pass':
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        return new_state
    else:
        old_pos, new_pos = action.split(' to ')
        old_pos = tuple(map(int, old_pos.split(',')))
        new_pos = tuple(map(int, new_pos.split(',')))
        
        # Check if the move is valid
        if not is_within_bounds(new_pos) or (new_pos in state['blue_units'] or new_pos in state['red_units']):
            raise ValueError("Invalid move")
        
        # Update the positions of the units
        if old_pos in state['blue_units']:
            new_state['blue_units'].remove(old_pos)
            new_state['blue_units'].append(new_pos)
        elif old_pos in state['red_units']:
            new_state['red_units'].remove(old_pos)
            new_state['red_units'].append(new_pos)
        
        # Check for stun condition
        for unit in state['blue_units']:
            if abs(unit[0] - new_pos[0]) + abs(unit[1] - new_pos[1]) == 1:
                new_state['blue_units'].remove(unit)
                break
        
        for unit in state['red_units']:
            if abs(unit[0] - new_pos[0]) + abs(unit[1] - new_pos[1]) == 1:
                new_state['red_units'].remove(unit)
                break
        
        new_state['turn_count'] += 1
        return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return ['Blue', 'Red'][player_id]

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    if state['center_square_occupied']:
        return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    for unit in state['blue_units']:
        for i in range(5):
            for j in range(5):
                if (i, j) != unit and (i, j) not in state['blue_units'] and (i, j) not in state['red_units']:
                    legal_actions.append(f'move {unit} to {(i, j)}')
    for unit in state['red_units']:
        for i in range(5):
            for j in range(5):
                if (i, j) != unit and (i, j) not in state['blue_units'] and (i, j) not in state['red_units']:
                    legal_actions.append(f'move {unit} to {(i, j)}')
    if not legal_actions:
        legal_actions.append('pass')
    return legal_actions

# Get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    blue_obs = {'units': state['blue_units']}
    red_obs = {'units': state['red_units']}
    return [blue_obs, red_obs]

# Main function to simulate the game
def main():
    state = get_initial_state()
    while True:
        print(f"Current state: {state}")
        legal_actions = get_legal_actions(state)
        print(f"Legal actions: {legal_actions}")
        if not legal_actions:
            print("No legal moves, it's a draw!")
            break
        action = input("Choose your action: ")
        try:
            state = apply_action(state, action)
            if state['center_square_occupied']:
                print("Blue wins!")
                break
            if state['turn_count'] >= 50:
                print("Game ends in a draw!")
                break
        except ValueError as e:
            print(e)
        state = get_observations(state)

if __name__ == "__main__":
    main()