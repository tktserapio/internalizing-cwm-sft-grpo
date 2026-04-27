import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper functions
def shuffle_deck() -> list[int]:
    """Shuffles a standard 52-card deck and returns the shuffled order."""
    suits = ['S', 'C', 'D', 'H']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    deck = [(rank, suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return [deck.index(card) + 1 for card in deck]  # Adding 1 to convert to 1-based index

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = shuffle_deck()
    state = {
        'deck': deck,
        'upcard': None,
        'dealer': 0,
        'phase': 'Draw',
        'knock_card': 10,
        'knocked': False,
        'player_0_melds': [],
        'player_0_deadwood': [],
        'player_1_melds': [],
        'player_1_deadwood': [],
        'player_0_hand': deck[:5],
        'player_1_hand': deck[5:10],
        'player_0_score': 0,
        'player_1_score': 0
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['upcard'] = state['deck'].pop(0)
        new_state['phase'] = 'Discard'
    elif action == 'Draw upcard':
        new_state['upcard'] = state['deck'].pop(0)
        new_state['phase'] = 'Discard'
    elif action.startswith('Action: '):
        card_index = int(action.split(': ')[1])
        new_state['player_0_hand'][card_index] = state['deck'].pop(0)
        new_state['phase'] = 'Discard'
    elif action == 'Action: Knock':
        new_state['knocked'] = True
        new_state['phase'] = 'Layoff'
        new_state['knock_card'] = 10
        new_state['player_0_deadwood'] = [card[1] for card in state['player_0_hand'] if card not in new_state['player_0_melds']]
        new_state['player_1_deadwood'] = [card[1] for card in state['player_1_hand'] if card not in new_state['player_1_melds']]
    elif action == 'Action: Done':
        new_state['knocked'] = True
        new_state['phase'] = 'Layoff'
        new_state['knock_card'] = 10
        new_state['player_0_deadwood'] = [card[1] for card in state['player_0_hand'] if card not in new_state['player_0_melds']]
        new_state['player_1_deadwood'] = [card[1] for card in state['player_1_hand'] if card not in new_state['player_1_melds']]
    elif action == 'Pass':
        new_state['phase'] = 'Layoff'
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['knocked']:
        return -4
    return state['dealer']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['knocked']:
        return [state['player_0_score'], state['player_1_score']]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['knocked']:
        return []
    if state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    if state['phase'] == 'Discard':
        if state['knocked']:
            return ['Action: Knock', 'Action: Done']
        return ['Action: 2c', 'Action: 3d', 'Action: 4s', 'Action: 5h', 'Action: Done', 'Pass']
    return []

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        'upcard': state['upcard'],
        'dealer': state['dealer'],
        'deck': state['deck'],
        'knock_card': state['knock_card'],
        'knocked': state['knocked'],
        'phase': state['phase'],
        'player_0_melds': state['player_0_melds'],
        'player_0_deadwood': state['player_0_deadwood'],
        'player_1_melds': state['player_1_melds'],
        'player_1_deadwood': state['player_1_deadwood'],
        'player_0_hand': state['player_0_hand'],
        'player_1_hand': state['player_1_hand']
    }
    player_1_obs = {
        'upcard': state['upcard'],
        'dealer': state['dealer'],
        'deck': state['deck'],
        'knock_card': state['knock_card'],
        'knocked': state['knocked'],
        'phase': state['phase'],
        'player_0_melds': state['player_0_melds'],
        'player_0_deadwood': state['player_0_deadwood'],
        'player_1_melds': state['player_1_melds'],
        'player_1_deadwood': state['player_1_deadwood'],
        'player_0_hand': state['player_1_hand'],
        'player_1_hand': state['player_0_hand']
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ['Draw stock', 'Action: 2c', 'Action: 3d', 'Action: 4s', 'Action: 5h', 'Action: Done']
    else:
        return ['Draw stock', 'Action: 2c', 'Action: 3d', 'Action: 4s', 'Action: 5h', 'Action: Done']