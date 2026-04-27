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
        'current_player': 0,
        'publicly_revealed_cards': []
    }
    return state

# Apply an action to the game state
def apply_action(state: State, action: Action) -> State:
    if action.startswith('deal:'):
        # Handle chance actions
        state['deck'] = action.split(':')[1].split(',')
        state['player0_cards'] = state['deck'][:8]
        state['player1_cards'] = state['deck'][8:]
        state['player0_hand'] = state['player0_cards'][:3]
        state['player1_hand'] = state['player1_cards'][:3]
        state['current_player'] = 0
        return state
    
    if action.startswith('play:'):
        # Handle player actions
        card_index = int(action.split(':')[1])
        player_id = state['current_player']
        
        if player_id == 0:
            player_hand = state['player0_hand']
            player_win_pile = state['player0_win_pile']
            player_cards = state['player0_cards']
        else:
            player_hand = state['player1_hand']
            player_win_pile = state['player1_win_pile']
            player_cards = state['player1_cards']
        
        # Remove the chosen card from the hand
        chosen_card = player_hand.pop(card_index)
        player_hand.sort()
        
        # Determine the winner of the battle
        opponent_card = state[f'player{1-player_id}_hand'][card_index]
        if chosen_card > opponent_card:
            player_win_pile.append(chosen_card)
            player_win_pile.append(opponent_card)
        elif chosen_card < opponent_card:
            player_win_pile.append(opponent_card)
            player_win_pile.append(chosen_card)
        else:
            # Showdown
            showdown_cards = [player_hand.pop(card_index), state[f'player{1-player_id}_hand'].pop(card_index)]
            while showdown_cards[0] == showdown_cards[1]:
                showdown_cards = [player_hand.pop(card_index), state[f'player{1-player_id}_hand'].pop(card_index)]
            
            # Determine the winner of the showdown
            showdown_winner = showdown_cards.index(max(showdown_cards))
            player_win_pile.extend(showdown_cards)
        
        # Replenish hands
        player_hand.extend(state[f'player{1-player_id}_cards'][:3])
        player_hand.sort()
        state[f'player{1-player_id}_hand'] = player_hand
        
        # Switch to the other player
        state['current_player'] = 1 - state['current_player']
        return state
    
    raise ValueError("Invalid action")

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}'

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    player0_win_pile = len(state['player0_win_pile'])
    player1_win_pile = len(state['player1_win_pile'])
    if player0_win_pile + player1_win_pile == 16:
        return [1.0, 0.0] if player0_win_pile > player1_win_pile else [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    player_id = get_current_player(state)
    player_hand = state[f'player{player_id}_hand']
    player_cards = state[f'player{player_id}_cards']
    if player_hand:
        return [f'play:{i}' for i in range(len(player_hand))]
    else:
        return []

# Get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    player0_hand = state['player0_hand']
    player1_hand = state['player1_hand']
    player0_win_pile = state['player0_win_pile']
    player1_win_pile = state['player1_win_pile']
    return [
        {'hand': player0_hand, 'win_pile': player0_win_pile},
        {'hand': player1_hand, 'win_pile': player1_win_pile}
    ]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # This function would need to be implemented based on the specific requirements of the game.
    # For simplicity, we assume that the history is already valid.
    return obs_action_history[-1][1].split(',') if obs_action_history else []