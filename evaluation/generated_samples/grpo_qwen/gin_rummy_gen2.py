import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to generate a shuffled deck
def shuffle_deck() -> list[int]:
    suits = ['Spades', 'Clubs', 'Diamonds', 'Hearts']
    ranks = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
    deck = [(suit, rank) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

# Required Functions
def get_initial_state() -> State:
    # Initial state setup
    state = {
        'deck': shuffle_deck(),
        'upcard': None,
        'dealer': 0,
        'phase': 'Draw',
        'knock_card': 10,
        'knocked_by': None,
        'knock_phase': False,
        'player_0_melds': [],
        'player_1_melds': [],
        'player_0_deadwood': 0,
        'player_1_deadwood': 0,
        'player_0_hand': [],
        'player_1_hand': []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    # Apply action to the state
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['upcard'] = new_state['deck'].pop()
        new_state['phase'] = 'Discard'
    elif action.startswith('Action: '):
        card_to_discard = action.split(':')[1]
        new_state['player_0_hand'].remove(card_to_discard)
        new_state['player_1_hand'].remove(card_to_discard)
        new_state['player_0_deadwood'] += 1 if card_to_discard in ['A', 'J', 'Q', 'K'] else int(card_to_discard[1])
        new_state['player_1_deadwood'] += 1 if card_to_discard in ['A', 'J', 'Q', 'K'] else int(card_to_discard[1])
        new_state['phase'] = 'Knock'
    elif action == 'Knock':
        new_state['knock_phase'] = True
        new_state['knocked_by'] = get_current_player(new_state)
    elif action == 'Done':
        new_state['knock_phase'] = False
    elif action == 'Pass':
        new_state['phase'] = 'Knock'
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    # Determine the current player based on the dealer and phase
    if state['knock_phase']:
        return state['knocked_by']
    else:
        return state['dealer']

def get_player_name(player_id: int) -> str:
    # Return the name of the player
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    # Get rewards for the current state
    if state['knock_phase']:
        return [state['player_1_deadwood'], state['player_0_deadwood']]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    # Get legal actions for the current state
    legal_actions = []
    if state['phase'] == 'Draw':
        legal_actions.append('Draw stock')
        legal_actions.append('Draw upcard')
    elif state['phase'] == 'Knock':
        if state['knock_phase']:
            legal_actions.append('Action: 1c')  # Example of declaring a meld
            legal_actions.append('Action: Knock')
            legal_actions.append('Action: Done')
        else:
            legal_actions.append('Pass')
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    # Get observations for each player
    player_0_obs = {
        'deck': state['deck'],
        'upcard': state['upcard'],
        'dealer': state['dealer'],
        'phase': state['phase'],
        'knock_phase': state['knock_phase'],
        'knocked_by': state['knocked_by'],
        'knock_card': state['knock_card'],
        'player_0_melds': state['player_0_melds'],
        'player_1_melds': state['player_1_melds'],
        'player_0_deadwood': state['player_0_deadwood'],
        'player_1_deadwood': state['player_1_deadwood'],
        'player_0_hand': state['player_0_hand'],
        'player_1_hand': state['player_1_hand']
    }
    player_1_obs = {
        'deck': state['deck'],
        'upcard': state['upcard'],
        'dealer': state['dealer'],
        'phase': state['phase'],
        'knock_phase': state['knock_phase'],
        'knocked_by': state['knocked_by'],
        'knock_card': state['knock_card'],
        'player_0_melds': state['player_1_melds'],
        'player_1_melds': state['player_0_melds'],
        'player_0_deadwood': state['player_1_deadwood'],
        'player_1_deadwood': state['player_0_deadwood'],
        'player_0_hand': state['player_1_hand'],
        'player_1_hand': state['player_0_hand']
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # Resample a valid sequence of actions
    history = obs_action_history[player_id]
    if len(history) > 0 and history[-1][1] is None:
        # If the last action was a pass, we need to add a draw action
        history.append(('Draw stock', None))
    return history