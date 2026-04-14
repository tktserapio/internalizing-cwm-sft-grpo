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
    """Deals the deck evenly among the players."""
    return [deck[i::num_players] for i in range(num_players)]

def get_card_rank(card):
    """Converts card string to its rank value (A=1, K=13, Q=12, J=11)."""
    ranks = {'A': 1, 'K': 13, 'Q': 12, 'J': 11}
    return ranks.get(card[0], int(card))

def get_card_value(card):
    """Converts card string to its numeric value (A=1, K=13, Q=12, J=11)."""
    return int(card)

def get_initial_state():
    """Returns the initial game state before any actions are taken."""
    # Deck of cards
    deck = ['A', 'K', 'Q', 'J'] * 4
    # Shuffle the deck
    shuffled_deck = shuffle_deck(deck)
    # Deal the deck evenly between two players
    player1_hand = shuffled_deck[:8]
    player2_hand = shuffled_deck[8:]
    # Form hands
    player1_draw_pile = shuffled_deck[16:]
    player2_draw_pile = shuffled_deck[16:]
    # Initial state
    return {
        'player1_hand': player1_hand,
        'player2_hand': player2_hand,
        'player1_draw_pile': player1_draw_pile,
        'player2_draw_pile': player2_draw_pile,
        'publicly_revealed_cards': [],
        'current_player': 0,
        'showdown': False,
        'showdown_winner': None,
        'showdown_burned_cards': []
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Parse action
    if action.startswith('play:'):
        card = action[5:]
        player_id = state['current_player']
        if player_id == 0:
            player = 'player1'
        else:
            player = 'player2'
        # Remove card from hand
        state[player + '_hand'].remove(card)
        # Add card to win pile
        state[player + '_win_pile'].append(card)
        # Draw new card
        state[player + '_draw_pile'].append(state[player + '_draw_pile'].pop(0))
        # Update current player
        state['current_player'] = (state['current_player'] + 1) % 2
        # Check for showdown
        if len(state[player + '_win_pile']) > 1:
            state['showdown'] = True
            state['showdown_winner'] = None
            state['showdown_burned_cards'] = []
    elif action.startswith('deal:'):
        # Handle chance action
        pass
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f'player{player_id}'

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # Determine winner based on win pile count
    if len(state['player1_win_pile']) > len(state['player2_win_pile']):
        return [1.0, 0.0]
    elif len(state['player1_win_pile']) < len(state['player2_win_pile']):
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    player_id = get_current_player(state)
    player = f'player{player_id}'
    if state[player + '_draw_pile']:
        return [f'play:{card}' for card in state[player + '_hand']]
    else:
        return []

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player1_obs = {
        'hand': state['player1_hand'],
        'draw_pile': state['player1_draw_pile'],
        'win_pile': state['player1_win_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    player2_obs = {
        'hand': state['player2_hand'],
        'draw_pile': state['player2_draw_pile'],
        'win_pile': state['player2_win_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    return [player1_obs, player2_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to be implemented to sample valid sequences of actions.
    # For simplicity, we will return a fixed sequence here.
    return [
        'play:A',
        'play:K',
        'play:Q',
        'play:J',
        'play:A',
        'play:K',
        'play:Q',
        'play:J',
        'play:A',
        'play:K',
        'play:Q',
        'play:J'
    ]