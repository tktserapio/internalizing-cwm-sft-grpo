import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Dict, Any

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

def create_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial state setup
    deck = shuffle_deck()
    upcard = deck.pop()
    stockpile = deck[:]
    deadwood = {0: [], 1: []}
    melds = {0: [], 1: []}
    current_player = 0
    knock_card = 10  # Default knock card value
    return {
        'deck': deck,
        'upcard': upcard,
        'stockpile': stockpile,
        'deadwood': deadwood,
        'melds': melds,
        'current_player': current_player,
        'knock_card': knock_card,
        'phase': 'Draw'
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['stockpile'].append(new_state['upcard'])
        new_state['upcard'] = new_state['stockpile'].pop()
        new_state['phase'] = 'Discard'
    elif action == 'Draw upcard':
        new_state['upcard'] = new_state['stockpile'].pop()
        new_state['phase'] = 'Discard'
    elif action.startswith('Action: '):
        card_to_discard = action.split(':')[1]
        new_state['deadwood'][new_state['current_player']].append(card_to_discard)
        new_state['melds'][new_state['current_player']].append(card_to_discard)
        new_state['deck'].append(card_to_discard)
        new_state['stockpile'].extend([card_to_discard])
        new_state['current_player'] = 1 - new_state['current_player']
        new_state['phase'] = 'Draw'
    elif action == 'Knock':
        new_state['knock_card'] = 10  # Default knock card value
        new_state['phase'] = 'Knock'
    elif action == 'Done':
        new_state['phase'] = 'Layoff'
    elif action == 'Pass':
        new_state['phase'] = 'Wall'
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['phase'] != 'Layoff':
        return [0.0, 0.0]
    knocker_deadwood = sum([int(card[0]) for card in state['deadwood'][0]])
    opponent_deadwood = sum([int(card[0]) for card in state['deadwood'][1]])
    if knocker_deadwood == 0:
        return [0.0, 25.0]
    else:
        return [knocker_deadwood - opponent_deadwood, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    if state['phase'] == 'Draw':
        legal_actions.append('Draw stock')
        legal_actions.append('Draw upcard')
    elif state['phase'] == 'Knock':
        legal_actions.append('Knock')
        legal_actions.append('Done')
    elif state['phase'] == 'Layoff':
        legal_actions.append('Pass')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        'deck': state['deck'],
        'upcard': state['upcard'],
        'stockpile': state['stockpile'],
        'deadwood': state['deadwood'][0],
        'melds': state['melds'][0],
        'knock_card': state['knock_card'],
        'current_player': state['current_player']
    }
    player_1_obs = {
        'deck': state['deck'],
        'upcard': state['upcard'],
        'stockpile': state['stockpile'],
        'deadwood': state['deadwood'][1],
        'melds': state['melds'][1],
        'knock_card': state['knock_card'],
        'current_player': 1 - state['current_player']
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ['Draw stock', 'Action: 3d', 'Knock']
    else:
        return ['Draw stock', 'Action: 3d', 'Knock']