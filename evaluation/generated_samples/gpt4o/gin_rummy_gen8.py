import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple
import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
SUITS = ['S', 'C', 'D', 'H']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
DECK = [f"{rank}{suit}" for suit in SUITS for rank in RANKS]
KNOCK_CARD_VALUE = 10
GIN_BONUS = 25
UNDERCUT_BONUS = 25

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = DECK.copy()
    random.shuffle(deck)
    player_hands = [deck[:10], deck[10:20]]
    stock_pile = deck[20:]
    discard_pile = [stock_pile.pop()]

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
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    current_player = new_state['current_player']
    player_hand = new_state['player_hands'][current_player]

    if action == "Draw stock":
        player_hand.append(new_state['stock_pile'].pop())
        new_state['phase'] = 'Discard'
    elif action == "Draw upcard":
        player_hand.append(new_state['discard_pile'].pop())
        new_state['phase'] = 'Discard'
    elif action.startswith("Action: "):
        card = action.split(": ")[1]
        if card in player_hand:
            player_hand.remove(card)
            new_state['discard_pile'].append(card)
            new_state['current_player'] = 1 - current_player
            new_state['phase'] = 'Draw'
    elif action == "Action: Knock":
        new_state['round_over'] = True
        # Handle scoring and round end logic here
    elif action == "Pass":
        new_state['current_player'] = 1 - current_player

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['round_over']:
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['round_over']:
        # Calculate rewards based on scoring logic
        return state['scores']
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['round_over']:
        return []

    current_player = state['current_player']
    phase = state['phase']
    player_hand = state['player_hands'][current_player]

    if phase == 'Draw':
        return ["Draw stock", "Draw upcard"]
    elif phase == 'Discard':
        actions = [f"Action: {card}" for card in player_hand]
        if calculate_deadwood(player_hand) <= KNOCK_CARD_VALUE:
            actions.append("Action: Knock")
        return actions
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {'hand': state['player_hands'][0], 'discard_pile': state['discard_pile']},
        {'hand': state['player_hands'][1], 'discard_pile': state['discard_pile']}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function would require more detailed implementation based on game history
    return []

def calculate_deadwood(hand: List[str]) -> int:
    """Calculates the deadwood value of a hand."""
    # Implement deadwood calculation logic
    return 0

# Helper functions to implement:
# - calculate_deadwood
# - scoring logic in apply_action
# - any additional game mechanics