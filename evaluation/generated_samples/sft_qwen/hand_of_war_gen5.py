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
    
    # Initial state dictionary
    state = {
        'deck': deck,
        'player0_cards': player0_cards,
        'player1_cards': player1_cards,
        'player0_win_pile': [],
        'player1_win_pile': [],
        'player0_draw_pile': player0_cards,
        'player1_draw_pile': player1_cards,
        'current_player': 0,
        'publicly_revealed_cards': []
    }
    return state

# Apply an action to the current state
def apply_action(state: State, action: Action) -> State:
    # Extract the card to play
    card_to_play = action.split(':')[1]
    
    # Check if the action is a chance action
    if action.startswith('deal'):
        # Deal cards from the deck
        cards_to_deal = action.split(',')[1:]
        state['deck'] = [card for card in state['deck'] if card not in cards_to_deal]
        state['player0_cards'].extend(cards_to_deal)
        state['player1_cards'].extend(cards_to_deal)
        state['player0_draw_pile'] = state['player0_cards']
        state['player1_draw_pile'] = state['player1_cards']
        return state
    
    # Check if the action is a play action
    if card_to_play in state['player0_cards']:
        # Remove the card from the player's hand
        state['player0_cards'].remove(card_to_play)
        state['player0_draw_pile'].append(card_to_play)
        
        # Determine the opponent's card
        opponent_card = state['player1_cards'][0]
        state['player1_cards'].pop(0)
        
        # Compare the cards
        if card_to_play > opponent_card:
            # Player 0 wins
            state['player0_win_pile'].append(card_to_play)
            state['player0_win_pile'].append(opponent_card)
        else:
            # Player 1 wins
            state['player1_win_pile'].append(opponent_card)
            state['player1_win_pile'].append(card_to_play)
        
        # Draw new cards
        state['player0_draw_pile'].extend(state['deck'][:3])
        state['player1_draw_pile'].extend(state['deck'][:3])
        state['deck'] = state['deck'][3:]
        
        # Switch to the other player's turn
        state['current_player'] = 1 if state['current_player'] == 0 else 0
        return state
    
    raise ValueError("Invalid action")

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    player0_win_pile = len(state['player0_win_pile'])
    player1_win_pile = len(state['player1_win_pile'])
    
    if player0_win_pile == 16:
        return [1.0, 0.0]
    elif player1_win_pile == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    player_id = get_current_player(state)
    player_cards = state[f'player{player_id}_cards']
    player_draw_pile = state[f'player{player_id}_draw_pile']
    publicly_revealed_cards = state['publicly_revealed_cards']
    
    if player_cards:
        return [f"play:{card}" for card in player_cards if card not in publicly_revealed_cards]
    else:
        return []

# Get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    player0_cards = state['player0_cards']
    player1_cards = state['player1_cards']
    player0_win_pile = state['player0_win_pile']
    player1_win_pile = state['player1_win_pile']
    
    return [
        {
            'cards': player0_cards,
            'win_pile': player0_win_pile,
            'draw_pile': state['player0_draw_pile'],
            'opponent_cards': player1_cards,
            'opponent_win_pile': player1_win_pile,
            'publicly_revealed_cards': state['publicly_revealed_cards']
        },
        {
            'cards': player1_cards,
            'win_pile': player1_win_pile,
            'draw_pile': state['player1_draw_pile'],
            'opponent_cards': player0_cards,
            'opponent_win_pile': player0_win_pile,
            'publicly_revealed_cards': state['publicly_revealed_cards']
        }
    ]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # This function would need to implement the logic to resample actions based on the observed history.
    # For simplicity, we will just return a fixed sequence of actions.
    # In a real implementation, this would involve stochastic sampling.
    if player_id == 0:
        return ['play:A', 'play:K', 'play:Q', 'play:J', 'play:A', 'play:K', 'play:Q', 'play:J']
    else:
        return ['play:A', 'play:K', 'play:Q', 'play:J', 'play:A', 'play:K', 'play:Q', 'play:J']