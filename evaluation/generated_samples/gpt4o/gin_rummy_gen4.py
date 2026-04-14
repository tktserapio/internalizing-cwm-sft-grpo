import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple, Dict
import random

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
SUITS = ['Spades', 'Clubs', 'Diamonds', 'Hearts']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
DECK = [f'{rank}{suit[0]}' for suit in SUITS for rank in RANKS]
KNOCK_CARD_VALUE = 10
GIN_BONUS = 25
UNDERCUT_BONUS = 25

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = DECK.copy()
    random.shuffle(deck)
    return {
        'deck': deck,
        'discard_pile': [],
        'hands': [deck[:10], deck[10:20]],
        'current_player': 0,
        'phase': 'Draw',
        'knock_card_value': KNOCK_CARD_VALUE,
        'scores': [0, 0]
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    current_player = new_state['current_player']
    if action.startswith("Draw"):
        if action == "Draw stock":
            card = new_state['deck'].pop(0)
        elif action == "Draw upcard":
            card = new_state['discard_pile'].pop()
        new_state['hands'][current_player].append(card)
        new_state['phase'] = 'Discard'
    elif action.startswith("Action: "):
        card = action.split(": ")[1]
        new_state['hands'][current_player].remove(card)
        new_state['discard_pile'].append(card)
        new_state['current_player'] = 1 - current_player
        new_state['phase'] = 'Draw'
    elif action == "Pass":
        new_state['current_player'] = 1 - current_player
    elif action == "Action: Knock":
        new_state['phase'] = 'Knock'
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    # Implement scoring logic based on the game rules
    return state['scores']

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['phase'] == 'Draw':
        actions = ['Draw stock']
        if state['discard_pile']:
            actions.append('Draw upcard')
    elif state['phase'] == 'Discard':
        actions = [f"Action: {card}" for card in state['hands'][state['current_player']]]
        if calculate_deadwood(state['hands'][state['current_player']]) <= state['knock_card_value']:
            actions.append("Action: Knock")
    else:
        actions = []
    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {'hand': state['hands'][0], 'discard_pile': state['discard_pile'], 'phase': state['phase']},
        {'hand': state['hands'][1], 'discard_pile': state['discard_pile'], 'phase': state['phase']}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # Implement logic to resample history based on observations
    return []

def calculate_deadwood(hand: List[str]) -> int:
    """Calculates the deadwood value of a hand."""
    deadwood_value = 0
    # Implement logic to calculate deadwood value
    return deadwood_value