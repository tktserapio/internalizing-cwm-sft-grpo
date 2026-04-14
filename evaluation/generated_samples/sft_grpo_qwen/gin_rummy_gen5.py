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

# Constants
DECK_SIZE = 52
KNOCK_CARD_VALUE = 10

# Helper functions
def initialize_deck() -> List[int]:
    """Initialize a shuffled deck of cards."""
    suits = ['Spades', 'Clubs', 'Diamonds', 'Hearts']
    ranks = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
    deck = []
    for suit in suits:
        for rank in ranks:
            deck.append((suit, rank))
    random.shuffle(deck)
    return deck

def initialize_upcard(deck: List[int]) -> int:
    """Initialize the upcard from the deck."""
    return deck.pop()

def initialize_state(deck: List[int], upcard: int) -> State:
    """Return the initial game state before any actions are taken."""
    return {
        'deck': deck,
        'upcard': upcard,
        'dealer': 0,  # Assume player 0 is the dealer
        'knock_card_value': KNOCK_CARD_VALUE,
        'phase': 'Draw',
        'player_0_melds': [],
        'player_1_melds': [],
        'player_0_deadwood': 0,
        'player_1_deadwood': 0,
        'player_0_hand': [],
        'player_1_hand': [],
        'player_0_obs': {},
        'player_1_obs': {}
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    
    if action == 'Draw stock':
        new_state['deck'].append(new_state['upcard'])
        new_state['upcard'] = new_state['deck'].pop()
        new_state['phase'] = 'Discard'
    
    elif action == 'Draw upcard':
        new_state['upcard'] = new_state['deck'].pop()
        new_state['phase'] = 'Discard'
    
    elif action.startswith('Action: '):
        card_to_discard = int(action.split(':')[1])
        new_state['player_0_hand'].remove(card_to_discard)
        new_state['deck'].append(card_to_discard)
        new_state['phase'] = 'Knock'
    
    elif action == 'Action: Knock':
        new_state['phase'] = 'Knock'
        new_state['knock_card_value'] = KNOCK_CARD_VALUE
        new_state['knock_card'] = new_state['upcard']
    
    elif action == 'Action: Done':
        new_state['phase'] = 'Knock'
    
    elif action == 'Pass':
        new_state['phase'] = 'Knock'
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['dealer']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    player_0_reward = 0.0
    player_1_reward = 0.0
    
    if state['phase'] == 'Knock':
        player_0_reward = state['player_0_deadwood']
        player_1_reward = state['player_1_deadwood']
    
    return [player_0_reward, player_1_reward]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    
    if state['phase'] == 'Draw':
        legal_actions.extend(['Draw stock', 'Draw upcard'])
    
    elif state['phase'] == 'Knock':
        legal_actions.extend(['Action: Knock', 'Action: Done', 'Pass'])
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        'deadwood': state['player_0_deadwood'],
        'melds': state['player_0_melds'],
        'hand': state['player_0_hand'],
        'upcard': state['upcard']
    }
    
    player_1_obs = {
        'deadwood': state['player_1_deadwood'],
        'melds': state['player_1_melds'],
        'hand': state['player_1_hand'],
        'upcard': state['upcard']
    }
    
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # For simplicity, we'll just return a random action here
    return ['Draw stock', 'Action: 4c', 'Action: Knock']