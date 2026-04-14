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
    deck = ['A', 'K', 'Q', 'J'] * 4  # 16 cards in total
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
        'public_revealed_cards': [],
        'player0_win_pile': [],
        'player1_win_pile': []
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    public_revealed_cards = state['public_revealed_cards']
    current_player = new_state['current_player']
    
    if action.startswith('play:'):
        card = action.split(':')[1]
        if card in state[f'player{current_player}_cards']:
            new_state[f'player{current_player}_cards'].remove(card)
            new_state[f'public_revealed_cards'].append(card)
            new_state['current_player'] = (current_player + 1) % 2
            return new_state
        else:
            raise ValueError(f"Invalid card {card} played.")
    elif action.startswith('deal:'):
        dealt_cards = action.split(':')[1].split(',')
        for card in dealt_cards:
            if card in state['deck']:
                state[f'player{current_player}_cards'].append(card)
                state['deck'].remove(card)
        new_state['current_player'] = (current_player + 1) % 2
        return new_state
    else:
        raise ValueError("Invalid action format.")

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
    current_player = get_current_player(state)
    player_cards = state[f'player{current_player}_cards']
    if not player_cards:
        return []  # Player's hand is empty, no legal actions
    if current_player == 0:
        return ['play:' + card for card in player_cards] + ['deal:' + ','.join(player_cards)]
    else:
        return ['play:' + card for card in player_cards] + ['deal:' + ','.join(player_cards)]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player0_obs = {
        'deck': state['deck'],
        'cards_in_hand': state['player0_cards'],
        'public_revealed_cards': state['public_revealed_cards'],
        'win_pile': state['player0_win_pile']
    }
    player1_obs = {
        'deck': state['deck'],
        'cards_in_hand': state['player1_cards'],
        'public_revealed_cards': state['public_revealed_cards'],
        'win_pile': state['player1_win_pile']
    }
    return [player0_obs, player1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement the logic to resample history based on the observations.
    # For simplicity, we will just return a random action for demonstration purposes.
    if obs_action_history[-1][1] is None:
        # If last action was a chance action, pick a random card to play
        player_cards = obs_action_history[-1][0]['cards_in_hand']
        return ['play:' + random.choice(player_cards)]
    else:
        # If last action was a play action, return the same action
        return [obs_action_history[-1][1]]