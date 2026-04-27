import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Dict, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def shuffle_deck() -> List[int]:
    """Shuffles the deck and returns the shuffled deck as a list of card ranks."""
    suits = ['S', 'C', 'D', 'H']
    ranks = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A']
    deck = [(suit, rank) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def create_initial_state(deck: List[Tuple[str, str]]) -> State:
    """Creates the initial state of the game."""
    # Initial state setup
    state = {
        'deck': deck,
        'upcard': None,
        'dealer': 0,  # Assume player 0 is the dealer
        'knocked': False,
        'knock_card': 10,  # Default knock card value
        'player_0_melds': [],
        'player_1_melds': [],
        'player_0_deadwood': 0,
        'player_1_deadwood': 0,
        'phase': 'Draw',
        'obs_action_history': []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Applies the given action to the state and returns the new state."""
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['deck'] = state['deck'][1:]  # Remove the last card from the deck
        new_state['upcard'] = new_state['deck'].pop()  # Draw the new upcard
        new_state['phase'] = 'Discard'
    elif action == 'Draw upcard':
        new_state['upcard'] = new_state['deck'].pop()  # Draw the new upcard
        new_state['phase'] = 'Discard'
    elif action.startswith('Action: '):
        card_to_discard = action.split(':')[1]
        if card_to_discard in new_state['deck']:
            new_state['deck'].remove(card_to_discard)
            new_state['phase'] = 'Knock'
        else:
            raise ValueError(f"Card {card_to_discard} not in deck")
    elif action == 'Action: Knock':
        new_state['knocked'] = True
        new_state['knock_card'] = new_state['player_1_deadwood']
        new_state['phase'] = 'Layoff'
        new_state['obs_action_history'].append(('Knock', action))
    elif action == 'Action: Done':
        new_state['phase'] = 'Done'
    elif action == 'Pass':
        new_state['phase'] = 'Done'
    else:
        raise ValueError(f"Invalid action: {action}")
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns the current player based on the dealer and knocked status."""
    if state['knocked']:
        return 1 - state['dealer']
    return state['dealer']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. For simplicity, assume no running rewards."""
    if state['phase'] == 'Done':
        return [0.0, 0.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for the current state."""
    if state['phase'] == 'Wall':
        return []
    if state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    if state['phase'] == 'Knock':
        return ['Action: Knock', 'Action: Done']
    if state['phase'] == 'Layoff':
        return ['Action: Done']
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns the observations for each player."""
    player_0_obs = {
        'upcard': state['upcard'],
        'deck': state['deck'],
        'dealer': state['dealer'],
        'knocked': state['knocked'],
        'knock_card': state['knock_card'],
        'player_0_melds': state['player_0_melds'],
        'player_1_melds': state['player_1_melds'],
        'player_0_deadwood': state['player_0_deadwood'],
        'player_1_deadwood': state['player_1_deadwood'],
        'phase': state['phase'],
        'obs_action_history': state['obs_action_history']
    }
    player_1_obs = {
        'upcard': state['upcard'],
        'deck': state['deck'],
        'dealer': state['dealer'],
        'knocked': state['knocked'],
        'knock_card': state['knock_card'],
        'player_0_melds': state['player_1_melds'],
        'player_1_melds': state['player_0_melds'],
        'player_0_deadwood': state['player_1_deadwood'],
        'player_1_deadwood': state['player_0_deadwood'],
        'phase': state['phase'],
        'obs_action_history': state['obs_action_history']
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ['Draw stock', 'Action: 3d', 'Action: Knock']
    else:
        return ['Draw stock', 'Action: 3d', 'Action: Knock']

# Main functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = shuffle_deck()
    return create_initial_state(deck)

def apply_action(state: State, action: Action) -> State:
    """Applies the given action to the state and returns the new state."""
    return apply_action(state, action)

def get_current_player(state: State) -> int:
    """Returns the current player based on the dealer and knocked status."""
    return get_current_player(state)

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return get_player_name(player_id)

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. For simplicity, assume no running rewards."""
    return get_rewards(state)

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for the current state."""
    return get_legal_actions(state)

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns the observations for each player."""
    return get_observations(state)

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    return resample_history(obs_action_history, player_id)