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

# Helper function to initialize the game state
def get_initial_state():
    # Initialize the deck and deal cards
    deck = ['A', 'K', 'Q', 'J'] * 4  # Aces, Kings, Queens, Jacks
    random.shuffle(deck)
    player0_cards = deck[:8]
    player1_cards = deck[8:]
    
    # Initial state dictionary
    state = {
        'deck': deck,
        'player0_cards': player0_cards,
        'player1_cards': player1_cards,
        'public_revealed_cards': [],
        'player0_hand': player0_cards[:3],
        'player1_hand': player1_cards[:3],
        'player0_win_pile': [],
        'player1_win_pile': [],
        'player0_draw_pile': player0_cards[3:],
        'player1_draw_pile': player1_cards[3:],
        'current_player': 0,
        'showdown_round': False,
        'showdown_winner': None,
        'showdown_burned_cards': []
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    if action.startswith('play:'):
        card_index = int(action.split(':')[1])
        current_player = get_current_player(state)
        
        # Remove the chosen card from the hand
        if current_player == 0:
            state['player0_hand'].pop(card_index)
        else:
            state['player1_hand'].pop(card_index)
        
        # Add the card to the win pile of the current player
        if current_player == 0:
            state['player0_win_pile'].append(state['player0_hand'][card_index])
        else:
            state['player1_win_pile'].append(state['player1_hand'][card_index])
        
        # Draw a new card to replenish the hand
        if len(state['player0_hand']) < 3 or len(state['player1_hand']) < 3:
            if current_player == 0:
                state['player0_hand'].append(state['player0_draw_pile'].pop(0))
            else:
                state['player1_hand'].append(state['player1_draw_pile'].pop(0))
        
        # Check for showdown conditions
        if len(state['player0_hand']) == 0 or len(state['player1_hand']) == 0:
            if current_player == 0:
                state['showdown_round'] = True
            else:
                state['showdown_round'] = True
        
        # Update the current player
        state['current_player'] = (state['current_player'] + 1) % 2
    
    elif action.startswith('deal:'):
        # This is a chance action, which we will ignore for now
        pass
    
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards
def get_rewards(state: State) -> list[float]:
    # For simplicity, we assume no running rewards until the game ends
    return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> list[Action]:
    current_player = get_current_player(state)
    player_hand = state[f'player{current_player}_hand']
    player_win_pile = state[f'player{current_player}_win_pile']
    
    # Legal actions are 'play:<card>' where the card is in the hand
    legal_actions = []
    for card in player_hand:
        legal_actions.append(f'play:{player_hand.index(card)}')
    
    # If there's a showdown, add 'deal:<card1>,<card2>,...' as a chance action
    if state['showdown_round']:
        legal_actions.append('deal:A,K,Q,J')
    
    return legal_actions

# Get observations
def get_observations(state: State) -> list[PlayerObservation]:
    player0_hand = state['player0_hand']
    player1_hand = state['player1_hand']
    player0_win_pile = state['player0_win_pile']
    player1_win_pile = state['player1_win_pile']
    
    player0_observation = {
        'hand': player0_hand,
        'win_pile': player0_win_pile,
        'draw_pile': state['player0_draw_pile']
    }
    player1_observation = {
        'hand': player1_hand,
        'win_pile': player1_win_pile,
        'draw_pile': state['player1_draw_pile']
    }
    
    return [player0_observation, player1_observation]

# Resample history
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # This function would need to be implemented based on the specific game dynamics
    # For now, we just return a dummy list of actions
    return ['play:0'] * 10  # Dummy actions for demonstration purposes