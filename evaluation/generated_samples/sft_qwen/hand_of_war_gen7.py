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
    deck = ['A', 'K', 'Q', 'J'] * 4
    random.shuffle(deck)
    player0_cards = deck[:8]
    player1_cards = deck[8:]
    
    # Initial state
    state = {
        'deck': deck,
        'player0_cards': player0_cards,
        'player1_cards': player1_cards,
        'player0_hand': player0_cards[:3],
        'player1_hand': player1_cards[:3],
        'player0_win_pile': [],
        'player1_win_pile': [],
        'player0_draw_pile': player0_cards[3:],
        'player1_draw_pile': player1_cards[3:],
        'current_player': 0,
        'publicly_revealed_cards': []
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Extract the card to play
    card_to_play = action.split(':')[1]
    
    # Check if the action is a chance action
    if action.startswith('deal'):
        # Handle chance actions
        dealt_cards = action.split(',')[1:]
        state['deck'] = [card for card in state['deck'] if card not in dealt_cards]
        for i in range(2):
            state['player0_cards'].append(dealt_cards[i])
            state['player1_cards'].append(dealt_cards[i + 4])
        state['player0_hand'] = state['player0_cards'][:3]
        state['player1_hand'] = state['player1_cards'][:3]
        state['player0_draw_pile'] = state['player0_cards'][3:]
        state['player1_draw_pile'] = state['player1_cards'][3:]
        state['current_player'] = 0
        return state
    
    # Check if the player is out of cards
    if len(state['player0_hand']) == 0 or len(state['player1_hand']) == 0:
        return state
    
    # Get the current player
    current_player = state['current_player']
    
    # Play the card
    if current_player == 0:
        state['player0_hand'].remove(card_to_play)
        state['player0_win_pile'].append(card_to_play)
    else:
        state['player1_hand'].remove(card_to_play)
        state['player1_win_pile'].append(card_to_play)
    
    # Draw new cards
    state['player0_hand'].extend(state['player0_draw_pile'][:3])
    state['player1_hand'].extend(state['player1_draw_pile'][:3])
    state['player0_draw_pile'] = state['player0_draw_pile'][3:]
    state['player1_draw_pile'] = state['player1_draw_pile'][3:]
    
    # Switch the current player
    state['current_player'] = 1 - current_player
    return state

# Determine the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}'

# Get rewards
def get_rewards(state: State) -> list[float]:
    # Calculate the number of cards in each player's win pile
    player0_cards_in_win_pile = len(state['player0_win_pile'])
    player1_cards_in_win_pile = len(state['player1_win_pile'])
    
    # Determine the winner based on the rules
    if player0_cards_in_win_pile > player1_cards_in_win_pile:
        return [1.0, 0.0]
    elif player1_cards_in_win_pile > player0_cards_in_win_pile:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

# Get legal actions
def get_legal_actions(state: State) -> list[Action]:
    # Get the current player
    current_player = get_current_player(state)
    
    # Get the player's hand
    player_hand = state[f'player{current_player}_hand']
    
    # Check if the player has any cards left in their hand
    if len(player_hand) == 0:
        return []
    
    # Return the legal actions
    return [f'play:{card}' for card in player_hand]

# Get observations
def get_observations(state: State) -> list[PlayerObservation]:
    # Get the current player
    current_player = get_current_player(state)
    
    # Get the player's hand and win pile
    player_hand = state[f'player{current_player}_hand']
    player_win_pile = state[f'player{current_player}_win_pile']
    
    # Create the observation dictionary
    player_observation = {
        'hand': player_hand,
        'win_pile': player_win_pile
    }
    
    # Return the observations
    return [player_observation]

# Resample history
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # Sample a valid sequence of actions
    # For simplicity, we will just randomly pick an action from the possible actions
    possible_actions = get_legal_actions(resample_history.get_initial_state())
    sampled_action = random.choice(possible_actions)
    
    # Return the sampled action
    return [sampled_action]