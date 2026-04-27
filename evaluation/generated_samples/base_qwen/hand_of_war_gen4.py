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
    """Shuffles the given deck."""
    random.shuffle(deck)
    return deck

def deal_cards(deck, num_players):
    """Deals the deck evenly between the players."""
    return [deck[i::num_players] for i in range(num_players)]

def get_card_rank(card):
    """Converts a card string to its rank (A=1, K=13, Q=12, J=11)."""
    ranks = {'A': 1, 'K': 13, 'Q': 12, 'J': 11}
    return ranks.get(card[0], int(card))

def get_card_value(card):
    """Converts a card string to its value (A=1, K=13, Q=12, J=11)."""
    return int(card)

# Required Functions
def get_initial_state():
    """Returns the initial game state before any actions are taken."""
    # Deck of cards
    deck = ['A', 'K', 'Q', 'J'] * 4
    # Shuffle the deck
    shuffled_deck = shuffle_deck(deck)
    # Deal the deck evenly between two players
    player1_hand, player2_hand = deal_cards(shuffled_deck, 2)
    # Form hands
    player1_hand = player1_hand[:3]
    player2_hand = player2_hand[:3]
    # Initialize state
    state = {
        'player1_hand': player1_hand,
        'player2_hand': player2_hand,
        'player1_win_pile': [],
        'player2_win_pile': [],
        'current_player': 0,
        'draw_pile': shuffled_deck[6:],  # Remaining cards after dealing
        'publicly_revealed_cards': []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    if action.startswith('play:'):
        card_index = get_card_value(action.split(':')[1])
        if new_state['current_player'] == 0:
            new_state['player1_hand'].remove(new_state['player1_hand'][card_index])
            new_state['player1_win_pile'].append(new_state['player1_hand'][card_index])
            new_state['player1_hand'].append(new_state['publicly_revealed_cards'][card_index])
            new_state['publicly_revealed_cards'].remove(new_state['publicly_revealed_cards'][card_index])
        else:
            new_state['player2_hand'].remove(new_state['player2_hand'][card_index])
            new_state['player2_win_pile'].append(new_state['player2_hand'][card_index])
            new_state['player2_hand'].append(new_state['publicly_revealed_cards'][card_index])
            new_state['publicly_revealed_cards'].remove(new_state['publicly_revealed_cards'][card_index])
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
    elif action.startswith('deal:'):
        new_state['draw_pile'] = shuffle_deck([card for card in new_state['draw_pile'] if card not in new_state['publicly_revealed_cards']])
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    player1_win_pile = len(state['player1_win_pile'])
    player2_win_pile = len(state['player2_win_pile'])
    if player1_win_pile == 16 or player2_win_pile == 16:
        return [1.0, 0.0] if player1_win_pile > player2_win_pile else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = get_current_player(state)
    if current_player == -4:
        return []  # Terminal state
    if current_player == 0:
        return ['play:' + card for card in state['player1_hand']]
    else:
        return ['play:' + card for card in state['player2_hand']]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player1_obs = {
        'hand': state['player1_hand'],
        'win_pile': state['player1_win_pile']
    }
    player2_obs = {
        'hand': state['player2_hand'],
        'win_pile': state['player2_win_pile']
    }
    return [player1_obs, player2_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement the logic to sample a valid sequence of actions.
    # For simplicity, we will just return a fixed sequence of actions.
    # In a real implementation, this function should generate a valid sequence based on the history.
    return ['play:K', 'play:Q', 'play:A', 'play:K', 'play:Q', 'play:A']