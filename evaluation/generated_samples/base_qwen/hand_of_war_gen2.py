import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to initialize the game state
def get_initial_state():
    # Initialize the deck and deal cards
    deck = ['A', 'K', 'Q', 'J'] * 4
    random.shuffle(deck)
    player0_hand = deck[:3]
    player1_hand = deck[3:6]
    player0_draw = deck[6:12]
    player1_draw = deck[12:]
    
    # Initialize state dictionary
    state = {
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'player0_draw': player0_draw,
        'player1_draw': player1_draw,
        'player0_win_pile': [],
        'player1_win_pile': [],
        'current_player': 0,
        'publicly_revealed_cards': []
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    if action.startswith('play:'):
        card_index = int(action.split(':')[1])
        if state['current_player'] == 0:
            state['player0_hand'][card_index], state['player1_hand'][card_index] = state['player1_hand'][card_index], state['player0_hand'][card_index]
        else:
            state['player1_hand'][card_index], state['player0_hand'][card_index] = state['player0_hand'][card_index], state['player1_hand'][card_index]
        state['publicly_revealed_cards'].append(action)
        state['current_player'] = (state['current_player'] + 1) % 2
    elif action.startswith('deal:'):
        # This is a chance action, not implemented here
        pass
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}'

# Get rewards per player
def get_rewards(state: State) -> list[float]:
    player0_win_pile = len(state['player0_win_pile'])
    player1_win_pile = len(state['player1_win_pile'])
    if player0_win_pile == 16 or player1_win_pile == 16:
        return [1.0, 0.0] if player0_win_pile == 16 else [0.0, 1.0]
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    if state['current_player'] == 0:
        return ['play:' + str(i) for i in range(3)]
    else:
        return ['play:' + str(i) for i in range(3)]

# Get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    player0_obs = {
        'hand': state['player0_hand'],
        'draw': state['player0_draw'],
        'win_pile': state['player0_win_pile']
    }
    player1_obs = {
        'hand': state['player1_hand'],
        'draw': state['player1_draw'],
        'win_pile': state['player1_win_pile']
    }
    return [player0_obs, player1_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # For simplicity, we assume that the history is deterministic and we can predict the next action
    # In a real implementation, this would involve sampling from the possible actions
    if obs_action_history[-1][1] is None:
        # Player just finished their turn
        if player_id == 0:
            return ['play:' + str(random.randint(0, 2))]
        else:
            return ['play:' + str(random.randint(0, 2))]
    else:
        # Player just played an action
        return []

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    print("Legal Actions:", get_legal_actions(initial_state))
    print("Rewards:", get_rewards(initial_state))