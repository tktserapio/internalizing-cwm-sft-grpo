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

# Helper function to initialize the deck and deal cards
def initialize_deck_and_deal():
    deck = ['A', 'K', 'Q', 'J'] * 4  # Aces, Kings, Queens, Jacks
    random.shuffle(deck)
    player0_cards = deck[:8]
    player1_cards = deck[8:]
    return {'deck': deck, 'player0_cards': player0_cards, 'player1_cards': player1_cards}

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    state = initialize_deck_and_deal()
    return {
        'state': state,
        'current_player': 0,
        'publicly_revealed_cards': [],
        'player0_win_pile': [],
        'player1_win_pile': []
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    public_revealed_cards = state['publicly_revealed_cards']
    current_player = new_state['current_player']
    
    if action.startswith('play:'):
        card = action.split(':')[1]
        if card not in state[f'{current_player}_cards']:
            raise ValueError(f"Invalid card {card} played.")
        
        if len(state[f'{current_player}_cards']) == 3:
            new_state[f'{current_player}_cards'].remove(card)
            new_state['publicly_revealed_cards'].append(card)
            new_state[f'{current_player}_win_pile'].append(card)
            new_state['player0_win_pile'].extend(public_revealed_cards)
            new_state['player1_win_pile'].extend(public_revealed_cards)
            new_state['publicly_revealed_cards'] = []
            new_state['current_player'] = (current_player + 1) % 2
        else:
            new_state[f'{current_player}_cards'].remove(card)
            new_state['publicly_revealed_cards'].append(card)
            new_state[f'{current_player}_win_pile'].append(card)
            new_state['current_player'] = (current_player + 1) % 2
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    player0_win_pile = len(state['player0_win_pile'])
    player1_win_pile = len(state['player1_win_pile'])
    if player0_win_pile == 16 or player1_win_pile == 16:
        return [1.0, 0.0] if player0_win_pile == 16 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = state['current_player']
    player_cards = state[f'{current_player}_cards']
    if len(player_cards) == 3:
        return ['play:' + card for card in player_cards]
    return []

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player0_obs = {
        'deck': state['deck'],
        'cards': state['player0_cards'],
        'win_pile': state['player0_win_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    player1_obs = {
        'deck': state['deck'],
        'cards': state['player1_cards'],
        'win_pile': state['player1_win_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    return [player0_obs, player1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # For simplicity, we assume that the history is deterministic and we can directly map it to a sequence of actions.
    # In a real implementation, this would involve sampling from the possible sequences based on the observations.
    # Here, we just return a fixed sequence of actions that corresponds to the given history.
    # This is a placeholder implementation.
    return obs_action_history[-1][0]['publicly_revealed_cards']  # Assuming the last action was a showdown