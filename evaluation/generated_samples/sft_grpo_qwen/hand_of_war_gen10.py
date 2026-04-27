import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the state
def get_initial_state() -> State:
    # Initialize the state with shuffled deck and empty hands
    deck = ['A', 'K', 'Q', 'J'] * 4
    random.shuffle(deck)
    state = {
        'deck': deck,
        'draw_pile_0': deck[:3],
        'draw_pile_1': deck[3:6],
        'win_pile_0': [],
        'win_pile_1': [],
        'current_player': 0,
        'publicly_revealed_cards': []
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action.startswith('play:'):
        card_index = int(action.split(':')[1])
        new_state['publicly_revealed_cards'].append(state['deck'][card_index])
        new_state['deck'].pop(card_index)
        new_state['draw_pile_0'].append(state['deck'].pop(0))
        new_state['draw_pile_1'].append(state['deck'].pop(0))
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
    elif action.startswith('deal:'):
        cards_to_deal = action.split(':')[1].split(',')
        for card in cards_to_deal:
            new_state['deck'].append(card)
    else:
        raise ValueError(f"Unknown action: {action}")
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    return [len(state['win_pile_0']), len(state['win_pile_1'])]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    current_player = get_current_player(state)
    if current_player == 0:
        return ['play:' + str(i) for i in range(3)]
    else:
        return ['play:' + str(i) for i in range(3)]

# Get the observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    current_player = get_current_player(state)
    public_revealed_cards = state['publicly_revealed_cards']
    player_0_obs = {'deck': state['draw_pile_0'], 'win_pile': state['win_pile_0'], 'public_revealed_cards': public_revealed_cards}
    player_1_obs = {'deck': state['draw_pile_1'], 'win_pile': state['win_pile_1'], 'public_revealed_cards': public_revealed_cards}
    return [player_0_obs, player_1_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # For simplicity, we assume the history is deterministic and just return the last action
    last_action = obs_action_history[-1][1]
    if last_action is None:
        return ['deal:' + ','.join(state['deck']) for state in obs_action_history]
    else:
        return [last_action]