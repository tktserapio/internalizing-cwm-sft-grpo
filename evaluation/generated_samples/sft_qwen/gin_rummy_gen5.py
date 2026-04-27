import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import *

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to initialize the deck and shuffle it
def initialize_deck():
    suits = ['Spades', 'Clubs', 'Diamonds', 'Hearts']
    ranks = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
    deck = [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

# Function to create the initial state
def get_initial_state() -> State:
    # Initialize the deck and shuffle it
    deck = initialize_deck()
    # Deal the cards
    dealer_hand = deck[:26]
    non_dealer_hand = deck[26:]
    
    # Initial state
    state = {
        'dealer_hand': dealer_hand,
        'non_dealer_hand': non_dealer_hand,
        'upcard': None,
        'knock_card': None,
        'phase': 'Draw',
        'deadwood': {'player_0': 0, 'player_1': 0},
        'melds': {'player_0': [], 'player_1': []},
        'wall': [],
        'obs_action_history': []
    }
    return state

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['upcard'] = new_state['dealer_hand'].pop(0)
        new_state['phase'] = 'Discard'
    elif action == 'Draw upcard':
        new_state['upcard'] = new_state['non_dealer_hand'].pop(0)
        new_state['phase'] = 'Discard'
    elif action.startswith('Action: '):
        card_to_discard = action.split(':')[1]
        new_state['dealer_hand'].remove(card_to_discard)
        new_state['non_dealer_hand'].append(card_to_discard)
        new_state['phase'] = 'Knock'
    elif action == 'Knock':
        new_state['knock_card'] = new_state['upcard']
        new_state['phase'] = 'Layoff'
    elif action == 'Done':
        new_state['phase'] = 'Layoff'
    elif action == 'Pass':
        new_state['phase'] = 'Layoff'
    else:
        raise ValueError(f"Invalid action: {action}")
    
    return new_state

# Function to determine the current player
def get_current_player(state: State) -> int:
    return 0 if state['phase'] == 'Draw' else 1

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Function to get the rewards per player
def get_rewards(state: State) -> list[float]:
    deadwood_points = lambda deadwood: sum([10 if card['rank'] in 'JQK' else int(card['rank']) for card in deadwood])
    player_0_deadwood = deadwood_points(state['deadwood']['player_0'])
    player_1_deadwood = deadwood_points(state['deadwood']['player_1'])
    if state['phase'] == 'Wall':
        return [0.0, 0.0]
    elif state['phase'] == 'Layoff':
        return [player_1_deadwood - player_0_deadwood, player_0_deadwood - player_1_deadwood]
    else:
        return [0.0, 0.0]

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    current_player = get_current_player(state)
    if state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    elif state['phase'] == 'Knock':
        return ['Knock', 'Done']
    elif state['phase'] == 'Layoff':
        return ['Action: ' + card for card in state['dealer_hand']] + ['Pass']
    else:
        return []

# Function to get the observations for the current state
def get_observations(state: State) -> list[PlayerObservation]:
    current_player = get_current_player(state)
    player_0_obs = {
        'deadwood': state['deadwood']['player_0'],
        'melds': state['melds']['player_0'],
        'upcard': state['upcard'],
        'dealer_hand': state['dealer_hand'],
        'non_dealer_hand': state['non_dealer_hand'],
        'knock_card': state['knock_card'],
        'phase': state['phase'],
        'wall': state['wall']
    }
    player_1_obs = {
        'deadwood': state['deadwood']['player_1'],
        'melds': state['melds']['player_1'],
        'upcard': state['upcard'],
        'dealer_hand': state['dealer_hand'],
        'non_dealer_hand': state['non_dealer_hand'],
        'knock_card': state['knock_card'],
        'phase': state['phase'],
        'wall': state['wall']
    }
    return [player_0_obs, player_1_obs]

# Function to resample history
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # For simplicity, we'll just randomly select actions from the possible ones
    actions = get_legal_actions(resample_history.get_observations(obs_action_history[-1]))
    return [random.choice(actions) for _ in obs_action_history]