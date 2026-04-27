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

# Helper function to initialize the state
def get_initial_state():
    # Initialize the deck and deal the cards
    deck = ['A', 'K', 'Q', 'J'] * 4
    random.shuffle(deck)
    player0_hand = deck[:3]
    player1_hand = deck[3:6]
    player0_draw_pile = deck[6:]
    player1_draw_pile = deck[6:]
    
    # Initial state
    state = {
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'player0_draw_pile': player0_draw_pile,
        'player1_draw_pile': player1_draw_pile,
        'player0_win_pile': [],
        'player1_win_pile': [],
        'current_player': 0,
        'public_revealed_cards': []
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Split the action string to get the card value
    card_value = action.split(':')[1]
    
    # Update the current player
    if state['current_player'] == 0:
        state['player0_hand'].remove(card_value)
        state['player1_hand'].remove(card_value)
    else:
        state['player1_hand'].remove(card_value)
        state['player0_hand'].remove(card_value)
    
    # Determine the winner of the battle
    if card_value in state['player0_hand']:
        state['player0_hand'].append(card_value)
        state['player1_hand'].append(card_value)
    else:
        state['player1_hand'].append(card_value)
        state['player0_hand'].append(card_value)
    
    # Update the win piles
    if card_value in state['player0_hand']:
        state['player0_win_pile'].append(card_value)
    else:
        state['player1_win_pile'].append(card_value)
    
    # Draw new cards
    if state['current_player'] == 0:
        state['player0_hand'].extend(state['player0_draw_pile'][:3])
        state['player0_draw_pile'] = state['player0_draw_pile'][3:]
    else:
        state['player1_hand'].extend(state['player1_draw_pile'][:3])
        state['player1_draw_pile'] = state['player1_draw_pile'][3:]
    
    # Switch to the other player
    state['current_player'] = 1 - state['current_player']
    
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}'

# Get the rewards
def get_rewards(state: State) -> list[float]:
    # Calculate the number of cards in each player's win pile
    player0_win_pile_length = len(state['player0_win_pile'])
    player1_win_pile_length = len(state['player1_win_pile'])
    
    # Determine the winner based on the win pile length
    if player0_win_pile_length > player1_win_pile_length:
        return [1.0, 0.0]
    elif player1_win_pile_length > player0_win_pile_length:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

# Get the legal actions
def get_legal_actions(state: State) -> list[Action]:
    # Check if the game is over
    if len(state['player0_draw_pile']) == 0 and len(state['player1_draw_pile']) == 0:
        return []
    
    # Check if the current player has no cards left
    if len(state[f'player{state["current_player"]}_hand']) == 0:
        return []
    
    # Get the current player's hand
    current_player_hand = state[f'player{state["current_player"]}_hand']
    
    # Get the legal actions for the current player
    legal_actions = []
    for card in current_player_hand:
        legal_actions.append(f'play:{card}')
    
    return legal_actions

# Get the observations
def get_observations(state: State) -> list[PlayerObservation]:
    # Create observations for both players
    player0_obs = {
        'hand': state['player0_hand'],
        'win_pile': state['player0_win_pile'],
        'draw_pile': state['player0_draw_pile'],
        'public_revealed_cards': state['public_revealed_cards']
    }
    player1_obs = {
        'hand': state['player1_hand'],
        'win_pile': state['player1_win_pile'],
        'draw_pile': state['player1_draw_pile'],
        'public_revealed_cards': state['public_revealed_cards']
    }
    
    return [player0_obs, player1_obs]

# Resample history
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # Sample a valid sequence of actions
    # For simplicity, we will just return a random action from the legal actions
    legal_actions = get_legal_actions(resample_history.get_observations())
    return [random.choice(legal_actions)]