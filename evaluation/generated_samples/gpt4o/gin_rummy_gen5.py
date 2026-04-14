import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
SUITS = ['S', 'C', 'D', 'H']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
POINTS = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 10, 'Q': 10, 'K': 10}
KNOCK_THRESHOLD = 10
GIN_BONUS = 25
UNDERCUT_BONUS = 25

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = [rank + suit for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    player_hands = [deck[:10], deck[10:20]]
    stock_pile = deck[20:]
    discard_pile = [stock_pile.pop(0)]
    return {
        'player_hands': player_hands,
        'stock_pile': stock_pile,
        'discard_pile': discard_pile,
        'current_player': 0,
        'phase': 'Draw',
        'round_over': False,
        'scores': [0, 0]
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    new_state['player_hands'] = [hand.copy() for hand in state['player_hands']]
    new_state['stock_pile'] = state['stock_pile'].copy()
    new_state['discard_pile'] = state['discard_pile'].copy()

    current_player = state['current_player']
    hand = new_state['player_hands'][current_player]

    if action == 'Draw stock':
        card = new_state['stock_pile'].pop(0)
        hand.append(card)
        new_state['phase'] = 'Discard'
    elif action == 'Draw upcard':
        card = new_state['discard_pile'].pop()
        hand.append(card)
        new_state['phase'] = 'Discard'
    elif action.startswith('Action: '):
        card = action.split(': ')[1]
        hand.remove(card)
        new_state['discard_pile'].append(card)
        new_state['current_player'] = 1 - current_player
        new_state['phase'] = 'Draw'
    elif action == 'Action: Knock':
        new_state['round_over'] = True
        new_state['phase'] = 'Knock'

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state['round_over'] else state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state['round_over']:
        return [0.0, 0.0]

    # Calculate deadwood and determine scores
    player_hands = state['player_hands']
    deadwood_values = [calculate_deadwood(hand) for hand in player_hands]
    knocker = state['current_player']
    opponent = 1 - knocker

    if deadwood_values[knocker] == 0:
        # Going Gin
        state['scores'][knocker] += GIN_BONUS + deadwood_values[opponent]
    elif deadwood_values[knocker] < deadwood_values[opponent]:
        # Successful Knock
        state['scores'][knocker] += deadwood_values[opponent] - deadwood_values[knocker]
    else:
        # Undercut
        state['scores'][opponent] += UNDERCUT_BONUS + deadwood_values[knocker] - deadwood_values[opponent]

    return state['scores']

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['round_over']:
        return []

    current_player = state['current_player']
    phase = state['phase']
    hand = state['player_hands'][current_player]

    if phase == 'Draw':
        return ['Draw stock', 'Draw upcard']
    elif phase == 'Discard':
        return [f"Action: {card}" for card in hand] + ['Action: Knock']

    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {
            'hand': state['player_hands'][0],
            'discard_pile': state['discard_pile'],
            'stock_size': len(state['stock_pile']),
            'phase': state['phase']
        },
        {
            'hand': state['player_hands'][1],
            'discard_pile': state['discard_pile'],
            'stock_size': len(state['stock_pile']),
            'phase': state['phase']
        }
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This is a complex function that would require a detailed implementation
    # to reconstruct the game history. For simplicity, we will return an empty list.
    return []

def calculate_deadwood(hand: List[str]) -> int:
    """Calculates the deadwood value of a hand."""
    # This function should calculate the deadwood value by identifying melds
    # and summing the point values of non-meld cards.
    # Placeholder implementation:
    return sum(POINTS[card[0]] for card in hand)

# Note: The implementation of calculate_deadwood is simplified and should be expanded to identify melds.