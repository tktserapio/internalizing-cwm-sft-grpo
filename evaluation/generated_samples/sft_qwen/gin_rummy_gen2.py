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

# Helper functions
def shuffle_deck() -> list[int]:
    """Shuffles the deck and returns a list of card ranks."""
    suits = ['Spades', 'Clubs', 'Diamonds', 'Hearts']
    ranks = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A']
    deck = [(suit, rank) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def create_initial_state(deck: list[int]) -> State:
    """Creates the initial game state with a shuffled deck."""
    # Initialize state with deck and empty hands
    state = {
        'deck': deck,
        'upcard': None,
        'dealer': 0,
        'phase': 'Draw',
        'knock_card': 10,
        'knocked': False,
        'player_0_melds': [],
        'player_0_deadwood': [],
        'player_1_melds': [],
        'player_1_deadwood': [],
        'player_0_hand': [],
        'player_1_hand': []
    }
    # Deal cards to players
    for _ in range(10):
        state['player_0_hand'].append(state['deck'].pop())
        state['player_1_hand'].append(state['deck'].pop())
    return state

def apply_action(state: State, action: Action) -> State:
    """Applies an action to the state and returns the new state."""
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['upcard'] = new_state['deck'].pop()
        new_state['phase'] = 'Discard'
    elif action.startswith('Action: '):
        card = action[7:]
        new_state['player_0_hand'].remove(card)
        new_state['player_1_hand'].remove(card)
        new_state['upcard'] = card
        new_state['phase'] = 'Knock'
    elif action == 'Knock':
        new_state['knocked'] = True
        new_state['knock_card'] = 10
        new_state['phase'] = 'Layoff'
    elif action == 'Done':
        new_state['knocked'] = True
        new_state['phase'] = 'Layoff'
    elif action == 'Pass':
        new_state['phase'] = 'Draw'
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    """Returns the current player (0 or 1)."""
    return state['dealer']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. For simplicity, returns [0.0, 0.0] until meaningful reward information is available."""
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for the current state."""
    current_player = get_current_player(state)
    if state['phase'] == 'Wall':
        return []
    if state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    if state['phase'] == 'Knock':
        return ['Knock', 'Done', 'Pass']
    if state['phase'] == 'Layoff':
        return ['Action: ' + card for card in state[f'player_{current_player}_hand']] + ['Done']
    return []

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns the observations for each player."""
    player_0_obs = {
        'upcard': state['upcard'],
        'dealer': state['dealer'],
        'knock_card': state['knock_card'],
        'knocked': state['knocked'],
        'player_0_melds': state['player_0_melds'],
        'player_0_deadwood': state['player_0_deadwood'],
        'player_1_melds': state['player_1_melds'],
        'player_1_deadwood': state['player_1_deadwood'],
        'player_0_hand': state['player_0_hand'],
        'player_1_hand': state['player_1_hand']
    }
    player_1_obs = {
        'upcard': state['upcard'],
        'dealer': state['dealer'],
        'knock_card': state['knock_card'],
        'knocked': state['knocked'],
        'player_0_melds': state['player_1_melds'],
        'player_0_deadwood': state['player_1_deadwood'],
        'player_1_melds': state['player_0_melds'],
        'player_1_deadwood': state['player_0_deadwood'],
        'player_0_hand': state['player_1_hand'],
        'player_1_hand': state['player_0_hand']
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # This function would need to be implemented based on the observed history.
    # For simplicity, we'll just return a fixed sequence of actions.
    # Note: This is a placeholder and should be replaced with actual logic.
    return ['Draw stock', 'Action: 3d', 'Knock', 'Done']