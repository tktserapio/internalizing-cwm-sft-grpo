import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to create a standard deck of cards
def create_deck():
    suits = ['Spades', 'Clubs', 'Diamonds', 'Hearts']
    ranks = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
    deck = [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks]
    return deck

# Function to shuffle the deck
def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

# Function to initialize the game state
def get_initial_state():
    deck = create_deck()
    shuffled_deck = shuffle_deck(deck)
    upcard = shuffled_deck.pop(0)
    stockpile = shuffled_deck.copy()
    return {
        'upcard': upcard,
        'stockpile': stockpile,
        'discard_pile': [],
        'players': [{'hand': [], 'knocked': False, 'deadwood': 0}],
        'dealer': 0,
        'phase': 'Draw',
        'knock_card': 10,
        'round': 1
    }

# Function to apply an action to the game state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['stockpile'].append(new_state['discard_pile'].pop())
        new_state['phase'] = 'Draw'
    elif action == 'Draw upcard':
        new_state['upcard'] = new_state['stockpile'].pop()
        new_state['phase'] = 'Discard'
    elif action.startswith('Action: '):
        card_to_discard = action.split(':')[1]
        new_state['players'][new_state['dealer']]['hand'].remove(card_to_discard)
        new_state['discard_pile'].append(card_to_discard)
        new_state['phase'] = 'Discard'
    elif action == 'Knock':
        new_state['players'][new_state['dealer']]['knocked'] = True
        new_state['phase'] = 'Knock'
    elif action == 'Done':
        new_state['players'][new_state['dealer']]['knocked'] = True
        new_state['phase'] = 'Layoff'
    elif action == 'Pass':
        new_state['phase'] = 'Draw'
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

# Function to determine the current player
def get_current_player(state: State) -> int:
    return state['dealer']

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Function to get rewards for the current state
def get_rewards(state: State) -> List[float]:
    if state['phase'] == 'Wall':
        return [0.0, 0.0]
    return [0.0, 0.0]

# Function to get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    player_id = get_current_player(state)
    if state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    elif state['phase'] == 'Discard':
        return [f'Action: {card}' for card in state['players'][player_id]['hand']] + ['Knock', 'Pass']
    elif state['phase'] == 'Knock':
        return ['Done']
    elif state['phase'] == 'Layoff':
        return []
    else:
        raise ValueError("Invalid phase")

# Function to get observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    player_id = get_current_player(state)
    return [
        {
            'deadwood': state['players'][player_id]['deadwood'],
            'melds': state['players'][player_id]['melds'],
            'hand': state['players'][player_id]['hand'],
            'upcard': state['upcard'],
            'discard_pile': state['discard_pile'],
            'knock_card': state['knock_card'],
            'phase': state['phase']
        },
        {
            'deadwood': 0,
            'melds': [],
            'hand': [],
            'upcard': None,
            'discard_pile': [],
            'knock_card': None,
            'phase': state['phase']
        }
    ]

# Function to resample history
def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would need to be implemented based on the observed history
    # For simplicity, we'll just return a fixed sequence of actions
    return ['Draw stock', 'Action: 2c', 'Knock', 'Done']