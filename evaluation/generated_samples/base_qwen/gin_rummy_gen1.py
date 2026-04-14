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
    """Shuffles the deck and returns the sorted list of card values."""
    deck = list(range(1, 53))  # 1-13 for each suit (Ace through King)
    random.shuffle(deck)
    return deck

def parse_card(card: int) -> str:
    """Converts a card index to a string representation."""
    suits = ['S', 'C', 'D', 'H']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    suit = suits[(card - 1) // 13]
    rank = ranks[card % 13]
    return f"{rank}{suit}"

def parse_meld(meld: List[int]) -> str:
    """Converts a list of card indices to a string representation of a meld."""
    meld_str = ''
    for card in meld:
        meld_str += parse_card(card)
    return meld_str

def parse_deadwood(deadwood: List[int]) -> str:
    """Converts a list of card indices to a string representation of deadwood."""
    deadwood_str = ''
    for card in deadwood:
        deadwood_str += parse_card(card)
    return deadwood_str

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial state setup
    deck = shuffle_deck()
    upcard = deck.pop(0)  # First upcard
    stockpile = deck.copy()
    deadwood = []
    melds = {}
    player_id = 0  # Non-dealer starts first
    state = {
        'deck': deck,
        'upcard': upcard,
        'stockpile': stockpile,
        'deadwood': deadwood,
        'melds': melds,
        'player_id': player_id,
        'phase': 'Draw',
        'knock_card': 10,
        'knocked': False
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    if action == 'Draw stock':
        state['stockpile'].append(state['upcard'])
        state['upcard'] = state['stockpile'].pop(0)
        state['phase'] = 'Discard'
    elif action == 'Draw upcard':
        state['stockpile'].append(state['upcard'])
        state['upcard'] = state['stockpile'].pop(0)
        state['phase'] = 'Discard'
    elif action.startswith('Action: '):
        card_to_discard = int(action[7:])
        state['deadwood'].append(card_to_discard)
        state['melds'][card_to_discard] = state['melds'].get(card_to_discard, [])
        state['player_id'] = (state['player_id'] + 1) % 2
        state['phase'] = 'Knock'
    elif action == 'Knock':
        state['knocked'] = True
        state['phase'] = 'Layoff'
    elif action == 'Done':
        state['phase'] = 'Layoff'
    elif action == 'Pass':
        state['phase'] = 'Layoff'
    else:
        raise ValueError(f"Invalid action: {action}")
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['player_id']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['phase'] == 'Wall':
        return [0.0, 0.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['phase'] == 'Wall':
        return []
    if state['player_id'] == state['knocked']:
        return ['Knock', 'Done']
    if state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    return ['Knock', 'Pass']

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        'deck': state['deck'],
        'upcard': state['upcard'],
        'stockpile': state['stockpile'],
        'deadwood': parse_deadwood(state['deadwood']),
        'melds': state['melds'],
        'player_id': state['player_id'],
        'phase': state['phase'],
        'knock_card': state['knock_card'],
        'knocked': state['knocked']
    }
    player_1_obs = {
        'deck': state['deck'],
        'upcard': state['upcard'],
        'stockpile': state['stockpile'],
        'deadwood': parse_deadwood(state['deadwood']),
        'melds': state['melds'],
        'player_id': state['player_id'],
        'phase': state['phase'],
        'knock_card': state['knock_card'],
        'knocked': state['knocked']
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Implementing resampling logic here would require a more complex algorithm
    # For simplicity, we'll just return a dummy action
    return ['Draw stock']