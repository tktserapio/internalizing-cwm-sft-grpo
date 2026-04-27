import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

def shuffle_deck() -> List[int]:
    """Shuffles the deck and returns a list of card ranks."""
    suits = ['S', 'C', 'D', 'H']
    ranks = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A']
    deck = [(rank, suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def create_initial_state(deck: List[int]) -> State:
    """Creates the initial game state."""
    return {
        'deck': deck,
        'upcard': None,
        'dealer': 0,
        'knock_card': 10,
        'phase': 'Draw',
        'player_0_hand': [],
        'player_1_hand': [],
        'player_0_melds': [],
        'player_1_melds': [],
        'player_0_deadwood': 0,
        'player_1_deadwood': 0,
        'player_0_score': 0,
        'player_1_score': 0,
        'obs_action_history': []
    }

def apply_action(state: State, action: Action) -> State:
    """Applies the given action to the state and returns the new state."""
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['upcard'] = new_state['deck'].pop()
        new_state['phase'] = 'Discard'
    elif action == 'Draw upcard':
        new_state['upcard'] = state['deck'].pop()
        new_state['phase'] = 'Discard'
    elif action.startswith('Action: '):
        card_to_discard = action.split(':')[1]
        new_state['player_0_hand'].remove(card_to_discard)
        new_state['deck'].append(card_to_discard)
        new_state['phase'] = 'Knock'
    elif action == 'Knock':
        new_state['phase'] = 'Knock'
    elif action == 'Done':
        new_state['phase'] = 'Knock'
    elif action == 'Pass':
        new_state['phase'] = 'Knock'
    else:
        raise ValueError(f"Invalid action: {action}")
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns the current player ID (-4 for terminal state)."""
    if state['phase'] == 'Knock':
        return -4
    return state['dealer']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['phase'] == 'Knock':
        return [state['player_0_score'], state['player_1_score']]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for the current state. Empty list if terminal."""
    if state['phase'] == 'Wall':
        return []
    if state['phase'] == 'Knock':
        return ['Done']
    if state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    if state['phase'] == 'Discard':
        return ['Action: ' + card for card in state['player_0_hand']] + ['Knock', 'Pass']
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        'upcard': state['upcard'],
        'dealer': state['dealer'],
        'knock_card': state['knock_card'],
        'player_0_hand': state['player_0_hand'],
        'player_1_hand': state['player_1_hand'],
        'player_0_melds': state['player_0_melds'],
        'player_1_melds': state['player_1_melds'],
        'player_0_deadwood': state['player_0_deadwood'],
        'player_1_deadwood': state['player_1_deadwood'],
        'phase': state['phase'],
        'obs_action_history': state['obs_action_history']
    }
    player_1_obs = {
        'upcard': state['upcard'],
        'dealer': state['dealer'],
        'knock_card': state['knock_card'],
        'player_0_hand': state['player_1_hand'],
        'player_1_hand': state['player_0_hand'],
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
    return obs_action_history[-1][1]