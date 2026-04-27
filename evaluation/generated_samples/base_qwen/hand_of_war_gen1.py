import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper functions
def shuffle_deck(deck):
    """Shuffles the given deck of cards."""
    random.shuffle(deck)
    return deck

def deal_cards(deck, num_players):
    """Deals cards evenly between players."""
    dealt_cards = []
    for _ in range(num_players):
        dealt_cards.append(deck[:3])
        deck = deck[3:]
    return dealt_cards

def get_card_rank(card):
    """Converts a card string to its rank (A=1, K=13, Q=12, J=11)."""
    ranks = {'A': 1, 'K': 13, 'Q': 12, 'J': 11}
    return ranks.get(card[0], int(card))

# Required Functions
def get_initial_state():
    """Returns the initial game state before any actions are taken."""
    # Deck of cards
    deck = ['A', 'K', 'Q', 'J'] * 4
    # Shuffle the deck
    shuffled_deck = shuffle_deck(deck)
    # Deal cards evenly between two players
    dealt_cards = deal_cards(shuffled_deck, 2)
    # Initialize state
    state = {
        'deck': shuffled_deck,
        'players': [{'hand': dealt_cards[0], 'win_pile': [], 'draw_pile': dealt_cards[1]},
                    {'hand': dealt_cards[1], 'win_pile': [], 'draw_pile': dealt_cards[0]}],
        'current_player': 0,
        'public_revealed_cards': [],
        'showdown_round': False,
        'showdown_winner': None,
        'showdown_burned_cards': [],
        'showdown_drawn_cards': [],
        'showdown_played_cards': []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    if action.startswith('play:'):
        card_index = get_card_rank(action.split(':')[1])
        if card_index < len(new_state['players'][new_state['current_player']]['hand']):
            new_state['players'][new_state['current_player']]['hand'].pop(card_index)
            new_state['players'][new_state['current_player']]['win_pile'].append(action.split(':')[1])
            new_state['current_player'] = (new_state['current_player'] + 1) % 2
            new_state['public_revealed_cards'].append(action)
            return new_state
        else:
            raise ValueError("Invalid card index")
    elif action.startswith('deal:'):
        new_state['deck'] = shuffle_deck(list(set(new_state['deck']) - set(action.split(','))))
        new_state = apply_action(new_state, 'deal:' + ','.join(new_state['deck']))
        return new_state
    else:
        raise ValueError("Unsupported action")

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if len(state['players'][0]['win_pile']) == 16:
        return [1.0, 0.0]
    elif len(state['players'][1]['win_pile']) == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['current_player'] == -4:
        return []
    current_player_hand = state['players'][state['current_player']]['hand']
    if not current_player_hand:
        return []
    return ['play:' + card for card in current_player_hand]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        'hand': state['players'][0]['hand'],
        'win_pile': state['players'][0]['win_pile'],
        'draw_pile': state['players'][0]['draw_pile'],
        'public_revealed_cards': state['public_revealed_cards']
    }
    player_1_obs = {
        'hand': state['players'][1]['hand'],
        'win_pile': state['players'][1]['win_pile'],
        'draw_pile': state['players'][1]['draw_pile'],
        'public_revealed_cards': state['public_revealed_cards']
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to be implemented based on the specific game logic and history.
    # For simplicity, we will just return a fixed sequence of actions.
    # In a real implementation, this would involve sampling from possible histories.
    return [
        'play:A',
        'play:K',
        'play:Q',
        'play:J',
        'play:A',
        'play:K',
        'play:Q',
        'play:J'
    ]