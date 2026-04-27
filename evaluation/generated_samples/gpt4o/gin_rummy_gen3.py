import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple, Optional
import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
SUITS = ['S', 'C', 'D', 'H']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
DECK = [rank + suit for suit in SUITS for rank in RANKS]
KNOCK_CARD_VALUE = 10
GIN_BONUS = 25
UNDERCUT_BONUS = 25

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = DECK[:]
    random.shuffle(deck)
    hands = [deck[:10], deck[10:20]]
    stock_pile = deck[20:]
    discard_pile = [stock_pile.pop()]
    return {
        'hands': hands,
        'stock_pile': stock_pile,
        'discard_pile': discard_pile,
        'current_player': 0,
        'phase': 'Draw',
        'scores': [0, 0],
        'round_over': False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    hands = [hand[:] for hand in state['hands']]
    stock_pile = state['stock_pile'][:]
    discard_pile = state['discard_pile'][:]
    current_player = state['current_player']
    phase = state['phase']
    round_over = state['round_over']

    if action.startswith("Draw"):
        if action == "Draw stock":
            hands[current_player].append(stock_pile.pop())
        elif action == "Draw upcard":
            hands[current_player].append(discard_pile.pop())
        new_state['phase'] = 'Discard'
    elif action.startswith("Action: "):
        card = action.split(": ")[1]
        hands[current_player].remove(card)
        discard_pile.append(card)
        new_state['current_player'] = 1 - current_player
        new_state['phase'] = 'Draw'
    elif action == "Action: Knock":
        round_over = True
        new_state['phase'] = 'Knock'
    elif action == "Pass":
        new_state['current_player'] = 1 - current_player
    elif action == "Action: Done":
        round_over = True

    new_state.update({
        'hands': hands,
        'stock_pile': stock_pile,
        'discard_pile': discard_pile,
        'round_over': round_over
    })

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

    # Calculate rewards based on deadwood and bonuses
    # Placeholder: Implement scoring logic here
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['round_over']:
        return []

    phase = state['phase']
    legal_actions = []

    if phase == 'Draw':
        if state['stock_pile']:
            legal_actions.append("Draw stock")
        if state['discard_pile']:
            legal_actions.append("Draw upcard")
    elif phase == 'Discard':
        hand = state['hands'][state['current_player']]
        legal_actions.extend([f"Action: {card}" for card in hand])
        if calculate_deadwood(hand) <= KNOCK_CARD_VALUE:
            legal_actions.append("Action: Knock")

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {
            'hand': state['hands'][0],
            'discard_pile': state['discard_pile'],
            'stock_size': len(state['stock_pile']),
            'phase': state['phase']
        },
        {
            'hand': state['hands'][1],
            'discard_pile': state['discard_pile'],
            'stock_size': len(state['stock_pile']),
            'phase': state['phase']
        }
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # Placeholder: Implement resampling logic here
    return []

def calculate_deadwood(hand: List[str]) -> int:
    """Calculates the deadwood points for a given hand."""
    # Placeholder: Implement deadwood calculation logic here
    return 0

# Additional helper functions can be defined here to support the main functions.