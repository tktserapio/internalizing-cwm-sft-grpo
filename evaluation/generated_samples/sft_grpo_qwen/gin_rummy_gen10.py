import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def shuffle_deck() -> List[int]:
    """Shuffles the deck and returns a list of card ranks."""
    suits = ['S', 'C', 'D', 'H']
    ranks = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A']
    deck = [(rank, suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def create_initial_state(deck: List[Tuple[str, str]]) -> State:
    """Creates the initial game state."""
    # Initial state setup
    state = {
        'deck': deck,
        'upcard': None,
        'dealer': 0,
        'phase': 'Draw',
        'knock_card': 10,
        'knocked_by': None,
        'knock_phase': False,
        'player_0_melds': [],
        'player_0_deadwood': 0,
        'player_1_melds': [],
        'player_1_deadwood': 0,
        'player_0_hand': [],
        'player_1_hand': [],
        'player_0_score': 0,
        'player_1_score': 0
    }
    # Deal initial cards
    for _ in range(10):
        state['player_0_hand'].append(state['deck'].pop())
        state['player_1_hand'].append(state['deck'].pop())
    return state

def apply_action(state: State, action: Action) -> State:
    """Applies an action to the state and returns the new state."""
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['upcard'] = state['deck'].pop()
        new_state['phase'] = 'Discard'
    elif action == 'Draw upcard':
        new_state['upcard'] = state['player_0_hand'].pop()
        new_state['phase'] = 'Discard'
    elif action.startswith('Action: '):
        card_to_discard = action.split(':')[1]
        new_state['player_0_hand'].remove(card_to_discard)
        new_state['upcard'] = card_to_discard
        new_state['phase'] = 'Discard'
    elif action == 'Knock':
        new_state['knock_phase'] = True
        new_state['knocked_by'] = 0
        new_state['knock_phase'] = True
        new_state['knock_phase'] = True
    elif action == 'Done':
        new_state['knock_phase'] = False
    elif action == 'Pass':
        new_state['phase'] = 'Draw'
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    """Returns the current player (0 or 1), or -4 for terminal state."""
    if state['knock_phase']:
        return -4
    return state['dealer']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['knock_phase']:
        return [state['player_0_score'], state['player_1_score']]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['knock_phase']:
        return []
    if state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    if state['upcard'] is None:
        return ['Draw stock', 'Draw upcard', 'Pass']
    return ['Action: ' + card for card in state['player_0_hand']] + ['Knock', 'Done']

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        'phase': state['phase'],
        'upcard': state['upcard'],
        'dealer': state['dealer'],
        'knock_phase': state['knock_phase'],
        'knocked_by': state['knocked_by'],
        'knock_card': state['knock_card'],
        'player_0_melds': state['player_0_melds'],
        'player_0_deadwood': state['player_0_deadwood'],
        'player_1_melds': state['player_1_melds'],
        'player_1_deadwood': state['player_1_deadwood'],
        'player_0_hand': state['player_0_hand'],
        'player_1_hand': state['player_1_hand']
    }
    player_1_obs = {
        'phase': state['phase'],
        'upcard': state['upcard'],
        'dealer': (state['dealer'] + 1) % 2,
        'knock_phase': state['knock_phase'],
        'knocked_by': state['knocked_by'],
        'knock_card': state['knock_card'],
        'player_0_melds': state['player_1_melds'],
        'player_0_deadwood': state['player_1_deadwood'],
        'player_1_melds': state['player_0_melds'],
        'player_1_deadwood': state['player_0_deadwood'],
        'player_0_hand': state['player_1_hand'],
        'player_1_hand': state['player_0_hand']
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    if player_id == 0:
        # Player 0's history
        history = obs_action_history
    else:
        # Player 1's history
        history = obs_action_history[::-1]
    # Sample a valid sequence of actions
    sampled_actions = []
    for observation, action in history:
        if action is None:
            sampled_actions.append('Draw stock')
        else:
            sampled_actions.append(action)
    return sampled_actions

# Main functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = shuffle_deck()
    return create_initial_state(deck)

def apply_action(state: State, action: Action) -> State:
    """Applies an action to the state and returns the new state."""
    return apply_action(state, action)

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return get_current_player(state)

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return get_player_name(player_id)

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    return get_rewards(state)

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    return get_legal_actions(state)

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return get_observations(state)

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    return resample_history(obs_action_history, player_id)