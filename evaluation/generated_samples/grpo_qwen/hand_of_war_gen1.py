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

# Helper function to create a deck of cards
def create_deck() -> list[str]:
    ranks = ['A', 'K', 'Q', 'J']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    return [f"{rank} of {suit}" for suit in suits for rank in ranks]

# Initial state function
def get_initial_state() -> State:
    # Shuffle the deck
    deck = create_deck()
    random.shuffle(deck)
    
    # Deal the deck evenly between two players
    player1_cards = deck[:8]
    player2_cards = deck[8:]
    
    # Form hands
    player1_hand = player1_cards[:3]
    player2_hand = player2_cards[:3]
    
    # Initialize state
    state = {
        'deck': deck,
        'player1_hand': player1_hand,
        'player2_hand': player2_hand,
        'player1_win_pile': [],
        'player2_win_pile': [],
        'current_player': 0,
        'publicly_revealed_cards': []
    }
    return state

# Apply action function
def apply_action(state: State, action: Action) -> State:
    if action.startswith('play:'):
        card_index = int(action.split(':')[1])
        current_player = get_current_player(state)
        
        # Remove card from hand
        player_cards = state[f'player{current_player + 1}_hand']
        card_to_play = player_cards.pop(card_index)
        
        # Determine winner
        opponent_cards = state[f'player{(current_player + 1) % 2 + 1}_hand']
        opponent_card = opponent_cards.pop(0)
        
        # Compare cards
        if card_to_play > opponent_card:
            # Player 1 wins
            state[f'player1_win_pile'].append(card_to_play)
            state[f'player1_win_pile'].append(opponent_card)
            state[f'player2_hand'].insert(0, opponent_card)
        else:
            # Player 2 wins
            state[f'player2_win_pile'].append(card_to_play)
            state[f'player2_win_pile'].append(opponent_card)
            state[f'player1_hand'].append(opponent_card)
        
        # Draw new cards
        state[f'player{current_player + 1}_hand'] += state['deck'].pop(0)
        state[f'player{current_player + 1}_hand'] += state['deck'].pop(0)
        
        # Update current player
        state['current_player'] = (state['current_player'] + 1) % 2
        
        # Reset publicly revealed cards
        state['publicly_revealed_cards'] = []
        
        return state
    else:
        raise ValueError("Invalid action")

# Get current player function
def get_current_player(state: State) -> int:
    return state['current_player']

# Get player name function
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards function
def get_rewards(state: State) -> list[float]:
    player1_win_pile = len(state['player1_win_pile'])
    player2_win_pile = len(state['player2_win_pile'])
    
    # Check for terminal state
    if player1_win_pile == 16 or player2_win_pile == 16:
        return [1.0, 0.0] if player1_win_pile == 16 else [0.0, 1.0]
    elif player1_win_pile > player2_win_pile:
        return [1.0, 0.0]
    elif player2_win_pile > player1_win_pile:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

# Get legal actions function
def get_legal_actions(state: State) -> list[Action]:
    current_player = get_current_player(state)
    player_cards = state[f'player{current_player + 1}_hand']
    
    if player_cards:
        return [f'play:{i}' for i in range(len(player_cards))]
    else:
        return []

# Get observations function
def get_observations(state: State) -> list[PlayerObservation]:
    player1_hand = state['player1_hand']
    player2_hand = state['player2_hand']
    player1_win_pile = state['player1_win_pile']
    player2_win_pile = state['player2_win_pile']
    
    player1_obs = {
        'hand': player1_hand,
        'win_pile': player1_win_pile
    }
    player2_obs = {
        'hand': player2_hand,
        'win_pile': player2_win_pile
    }
    
    return [player1_obs, player2_obs]

# Resample history function
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # For simplicity, we assume the history is deterministic and just return the last action
    last_action = obs_action_history[-1][1]
    return [last_action] if last_action else []