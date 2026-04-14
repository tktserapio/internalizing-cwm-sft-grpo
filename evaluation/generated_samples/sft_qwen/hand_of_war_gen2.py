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

# Helper function to initialize the game state
def get_initial_state():
    # Initialize the deck
    deck = ['A', 'K', 'Q', 'J'] * 4
    
    # Shuffle the deck
    random.shuffle(deck)
    
    # Deal the deck evenly between two players
    player0_cards = deck[:8]
    player1_cards = deck[8:]
    
    # Form hands
    player0_hand = player0_cards[:3]
    player1_hand = player1_cards[:3]
    
    # Initialize state
    state = {
        'deck': deck,
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'player0_win_pile': [],
        'player1_win_pile': [],
        'player0_draw_pile': player0_cards[3:],
        'player1_draw_pile': player1_cards[3:],
        'current_player': 0,
        'publicly_revealed_cards': []
    }
    
    return state

# Apply action to the state
def apply_action(state: State, action: Action) -> State:
    # Parse the action
    if action.startswith('play:'):
        card_index = int(action.split(':')[1])
        player_id = 0 if state['current_player'] == 0 else 1
        
        # Remove the card from the player's hand
        state[f'player{player_id}_hand'][card_index] = None
        
        # Get the card value
        card_value = state[f'player{player_id}_draw_pile'].pop(0)
        
        # Add the card to the player's win pile
        state[f'player{player_id}_win_pile'].append(card_value)
        
        # Update the current player
        state['current_player'] = 1 if player_id == 0 else 0
        
        # Check if the game is over
        if len(state[f'player{player_id}_draw_pile']) == 0:
            state['current_player'] = -4  # Terminal state
            
    return state

# Determine the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}'

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    # Calculate the rewards based on the number of cards in the win piles
    player0_cards = len(state['player0_win_pile'])
    player1_cards = len(state['player1_win_pile'])
    
    if player0_cards > player1_cards:
        return [1.0, 0.0]
    elif player1_cards > player0_cards:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    player_id = get_current_player(state)
    player_hand = state[f'player{player_id}_hand']
    player_draw_pile = state[f'player{player_id}_draw_pile']
    
    if player_id == 0:
        return ['play:' + str(i) for i, card in enumerate(player_hand)]
    else:
        return ['deal:' + ','.join(player_draw_pile)]

# Get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    player0_hand = state['player0_hand']
    player1_hand = state['player1_hand']
    player0_win_pile = state['player0_win_pile']
    player1_win_pile = state['player1_win_pile']
    
    return [
        {
            'hand': player0_hand,
            'win_pile': player0_win_pile,
            'draw_pile': state['player0_draw_pile']
        },
        {
            'hand': player1_hand,
            'win_pile': player1_win_pile,
            'draw_pile': state['player1_draw_pile']
        }
    ]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would need to be implemented to stochastically sample a valid sequence of actions
    # For simplicity, we will just return a fixed sequence of actions
    # In a real implementation, this would involve sampling from the possible actions given the observations
    # Here, we assume a fixed sequence of actions for demonstration purposes
    if player_id == 0:
        return ['play:0', 'play:1', 'play:2', 'play:3', 'play:4', 'play:5', 'play:6', 'play:7']
    else:
        return ['play:0', 'play:1', 'play:2', 'play:3', 'play:4', 'play:5', 'play:6', 'play:7']