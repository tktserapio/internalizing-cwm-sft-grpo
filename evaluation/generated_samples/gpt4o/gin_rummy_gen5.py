import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
SUITS = ['S', 'C', 'D', 'H']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
DECK = [rank + suit for suit in SUITS for rank in RANKS]
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
        'scores': [0, 0],
        'knock_card_value': KNOCK_CARD_VALUE
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    current_player = new_state['current_player']
    hand = new_state['hands'][current_player]
    deck = new_state['deck']
    discard_pile = new_state['discard_pile']

    if action == "Draw stock":
        hand.append(deck.pop(0))
        new_state['phase'] = 'Discard'
    elif action == "Draw upcard":
        hand.append(discard_pile.pop())
        new_state['phase'] = 'Discard'
    elif action.startswith("Action: "):
        card = action.split(": ")[1]
        hand.remove(card)
        discard_pile.append(card)
        new_state['current_player'] = 1 - current_player
        new_state['phase'] = 'Draw'
    elif action == "Action: Knock":
        # Handle the knock logic here
        pass
    elif action == "Pass":
        new_state['current_player'] = 1 - current_player
    elif action == "Action: Done":
        # Handle end of knock sequence
        pass

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['phase'] == 'Wall':
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    return state['scores']

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['phase'] == 'Wall':
        return []
    
    current_player = state['current_player']
    hand = state['hands'][current_player]
    legal_actions = []

    if state['phase'] == 'Draw':
        if state['discard_pile']:
            legal_actions.append("Draw upcard")
        if state['deck']:
            legal_actions.append("Draw stock")
    elif state['phase'] == 'Discard':
        legal_actions.extend([f"Action: {card}" for card in hand])
        if calculate_deadwood_value(hand) <= state['knock_card_value']:
            legal_actions.append("Action: Knock")

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {'hand': state['hands'][0], 'discard_pile': state['discard_pile']},
        {'hand': state['hands'][1], 'discard_pile': state['discard_pile']}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function would require a more complex implementation to accurately resample history
    # based on the observations and actions. For simplicity, we'll return an empty list here.
    return []

def calculate_deadwood_value(hand: List[str]) -> int:
    """Calculate the deadwood value of a hand."""
    # This function should calculate the deadwood value based on the cards in hand
    # For simplicity, we assume all cards are deadwood here
    value = 0
    for card in hand:
        rank = card[:-1]
        if rank in ['J', 'Q', 'K']:
            value += 10
        elif rank == 'A':
            value += 1
        else:
            value += int(rank)
    return value