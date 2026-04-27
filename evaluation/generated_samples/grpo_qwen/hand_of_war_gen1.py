import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the state
def get_initial_state() -> State:
    # Initialize the state with the deck, hands, and other necessary variables
    deck = ['A', 'K', 'Q', 'J'] * 4  # Assuming a standard deck of 16 cards
    shuffled_deck = deck.copy()
    random.shuffle(shuffled_deck)
    
    player0_hand = shuffled_deck[:3]
    player1_hand = shuffled_deck[3:6]
    
    state = {
        'deck': shuffled_deck,
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'player0_win_pile': [],
        'player1_win_pile': [],
        'current_player': 0,
        'publicly_revealed_cards': []
    }
    return state

# Apply action function
def apply_action(state: State, action: Action) -> State:
    # Extract the player ID from the action string
    player_id = int(action.split(':')[1])
    
    # Check if the action is a chance action (dealing cards)
    if action.startswith('deal'):
        # Implement dealing cards logic here
        # For simplicity, we'll just shuffle the deck and deal new cards
        shuffled_deck = state['deck']
        random.shuffle(shuffled_deck)
        state['player0_hand'] = shuffled_deck[:3]
        state['player1_hand'] = shuffled_deck[3:6]
        return state
    
    # Check if the action is a regular play action
    if action.startswith('play'):
        # Extract the card value from the action string
        card_value = action.split(':')[1]
        
        # Determine the winner of the battle
        player0_card = state['player0_hand'][0]
        player1_card = state['player1_hand'][0]
        
        if card_value == player0_card:
            # Player 0 wins the battle
            state['player0_win_pile'].append(card_value)
            state['player1_win_pile'].append(player1_card)
            state['player1_win_pile'].append(player0_card)
        elif card_value == player1_card:
            # Player 1 wins the battle
            state['player1_win_pile'].append(card_value)
            state['player0_win_pile'].append(player0_card)
            state['player0_win_pile'].append(player1_card)
        else:
            # Higher card wins
            if card_value > player0_card:
                state['player0_win_pile'].append(card_value)
                state['player1_win_pile'].append(player1_card)
            else:
                state['player1_win_pile'].append(card_value)
                state['player0_win_pile'].append(player0_card)
        
        # Draw new cards
        state['player0_hand'] = state['deck'][:3]
        state['player1_hand'] = state['deck'][3:6]
        return state
    
    # Handle invalid actions
    raise ValueError("Invalid action")

# Get current player function
def get_current_player(state: State) -> int:
    return state['current_player']

# Get player name function
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards function
def get_rewards(state: State) -> List[float]:
    # Calculate rewards based on the number of cards in each player's win pile
    player0_win_pile = len(state['player0_win_pile'])
    player1_win_pile = len(state['player1_win_pile'])
    
    if player0_win_pile == 16:
        return [1.0, 0.0]
    elif player1_win_pile == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get legal actions function
def get_legal_actions(state: State) -> List[Action]:
    player_id = get_current_player(state)
    if player_id == 0:
        # Player 0's turn
        legal_actions = []
        for card in state['player0_hand']:
            legal_actions.append(f'play:{card}')
        return legal_actions
    elif player_id == 1:
        # Player 1's turn
        legal_actions = []
        for card in state['player1_hand']:
            legal_actions.append(f'play:{card}')
        return legal_actions
    else:
        # Terminal state
        return []

# Get observations function
def get_observations(state: State) -> List[PlayerObservation]:
    player0_hand = state['player0_hand']
    player1_hand = state['player1_hand']
    player0_win_pile = state['player0_win_pile']
    player1_win_pile = state['player1_win_pile']
    
    player0_obs = {
        'hand': player0_hand,
        'win_pile': player0_win_pile
    }
    player1_obs = {
        'hand': player1_hand,
        'win_pile': player1_win_pile
    }
    
    return [player0_obs, player1_obs]

# Resample history function
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would need to implement stochastic sampling of valid action sequences
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ['play:A', 'play:K', 'play:Q', 'play:J']
    elif player_id == 1:
        return ['play:K', 'play:Q', 'play:J', 'play:A']
    else:
        raise ValueError("Invalid player ID")