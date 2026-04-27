import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the state
def get_initial_state() -> State:
    # Initialize the state with the deck, hands, and other necessary variables
    deck = ['A', 'K', 'Q', 'J'] * 4  # Shuffle the deck
    random.shuffle(deck)
    player0_hand = deck[:3]
    player1_hand = deck[3:6]
    player0_win_pile = []
    player1_win_pile = []
    player0_draw_pile = deck[6:]
    player1_draw_pile = deck[6:]
    return {
        'deck': deck,
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'player0_win_pile': player0_win_pile,
        'player1_win_pile': player1_win_pile,
        'player0_draw_pile': player0_draw_pile,
        'player1_draw_pile': player1_draw_pile,
        'current_player': 0,
        'publicly_revealed_cards': [],
        'showdown_cards': [],
        'showdown_winner': None,
        'showdown_round': 0,
        'showdown_burn_card': None
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    if action.startswith('play:'):
        card = action.split(':')[1]
        if card in state['player0_hand']:
            state['player0_hand'].remove(card)
            state['player0_win_pile'].append(card)
        else:
            state['player1_hand'].remove(card)
            state['player1_win_pile'].append(card)
    elif action.startswith('deal:'):
        # For simplicity, we assume the deal action is not used in this game
        pass
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}'

# Get the rewards for the players
def get_rewards(state: State) -> List[float]:
    player0_win_pile_len = len(state['player0_win_pile'])
    player1_win_pile_len = len(state['player1_win_pile'])
    if player0_win_pile_len == 16:
        return [1.0, 0.0]
    elif player1_win_pile_len == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    player_id = get_current_player(state)
    if player_id == 0:
        return ['play:' + card for card in state['player0_hand']]
    else:
        return ['play:' + card for card in state['player1_hand']]

# Get the observations for the players
def get_observations(state: State) -> List[PlayerObservation]:
    player0_obs = {
        'hand': state['player0_hand'],
        'win_pile': state['player0_win_pile'],
        'draw_pile': state['player0_draw_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    player1_obs = {
        'hand': state['player1_hand'],
        'win_pile': state['player1_win_pile'],
        'draw_pile': state['player1_draw_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    return [player0_obs, player1_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Placeholder for resampling logic
    # For simplicity, we just return a fixed sequence of actions
    if player_id == 0:
        return ['play:A', 'play:K', 'play:Q', 'play:J']
    else:
        return ['play:J', 'play:Q', 'play:K', 'play:A']