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
    deck = ['A', 'K', 'Q', 'J'] * 4  # 16 cards total
    random.shuffle(deck)
    player0_cards = deck[:8]
    player1_cards = deck[8:]
    
    # Initial state dictionary
    state = {
        'deck': deck,
        'player0_cards': player0_cards,
        'player1_cards': player1_cards,
        'public_revealed_cards': [],
        'player0_win_pile': [],
        'player1_win_pile': [],
        'player0_draw_pile': player0_cards,
        'player1_draw_pile': player1_cards,
        'current_player': 0,
        'showdown_round': 0,
        'showdown_winner': None,
        'showdown_burn_card': None,
        'showdown_player0_card': None,
        'showdown_player1_card': None,
        'showdown_player0_draw_card': None,
        'showdown_player1_draw_card': None,
        'showdown_winner_cards': []
    }
    return state

# Apply an action to the current state
def apply_action(state: State, action: Action) -> State:
    if action.startswith('play:'):
        card_index = int(action.split(':')[1])
        player_id = state['current_player']
        if player_id == 0:
            player_cards = state['player0_cards']
        else:
            player_cards = state['player1_cards']
        
        # Remove the chosen card from the player's hand
        chosen_card = player_cards.pop(card_index)
        
        # Determine the winner of the battle
        if player_id == 0:
            opponent_cards = state['player1_cards']
        else:
            opponent_cards = state['player0_cards']
        
        # Check if the chosen card is higher than the opponent's card
        if chosen_card > max(opponent_cards):
            # Player wins the battle
            state['player0_win_pile'].append(chosen_card)
            state['player0_win_pile'].extend(opponent_cards)
            state['player1_win_pile'].extend(opponent_cards)
        elif chosen_card < max(opponent_cards):
            # Opponent wins the battle
            state['player1_win_pile'].append(max(opponent_cards))
            state['player1_win_pile'].extend(opponent_cards)
            state['player0_win_pile'].append(chosen_card)
        else:
            # Showdown occurs
            state['showdown_round'] += 1
            state['showdown_winner'] = None
            state['showdown_burn_card'] = chosen_card
            state['showdown_player0_card'] = player_cards.pop(0)
            state['showdown_player1_card'] = opponent_cards.pop(0)
            
            # Determine the winner of the showdown
            if state['showdown_player0_card'] > state['showdown_player1_card']:
                state['showdown_winner'] = 0
                state['showdown_winner_cards'] = [state['showdown_player0_card'], state['showdown_burn_card']]
            else:
                state['showdown_winner'] = 1
                state['showdown_winner_cards'] = [state['showdown_player1_card'], state['showdown_burn_card']]
                
            # Add the winners' cards to the respective win piles
            if state['showdown_winner'] == 0:
                state['player0_win_pile'].extend(state['showdown_winner_cards'])
                state['player0_win_pile'].extend(opponent_cards)
            else:
                state['player1_win_pile'].extend(state['showdown_winner_cards'])
                state['player1_win_pile'].extend(opponent_cards)
                
    else:
        raise ValueError("Invalid action: {}".format(action))
    
    # Update the current player
    state['current_player'] = (state['current_player'] + 1) % 2
    
    # Draw new cards if necessary
    if len(state['player0_cards']) < 3 or len(state['player1_cards']) < 3:
        if state['current_player'] == 0:
            state['player0_cards'].extend(state['deck'][:3])
            state['deck'] = state['deck'][3:]
        else:
            state['player1_cards'].extend(state['deck'][:3])
            state['deck'] = state['deck'][3:]
    
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards per player
def get_rewards(state: State) -> list[float]:
    player0_win_pile = state['player0_win_pile']
    player1_win_pile = state['player1_win_pile']
    
    # Calculate the rewards based on the size of the win piles
    if len(player0_win_pile) > len(player1_win_pile):
        return [1.0, 0.0]
    elif len(player0_win_pile) < len(player1_win_pile):
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

# Get legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    current_player = state['current_player']
    player_cards = state[f'player{current_player}_cards']
    public_revealed_cards = state['public_revealed_cards']
    
    # Check if the player has cards left in their hand
    if player_cards:
        return [f'play:{i}' for i in range(len(player_cards))]
    else:
        return []

# Get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    player0_cards = state['player0_cards']
    player1_cards = state['player1_cards']
    public_revealed_cards = state['public_revealed_cards']
    
    player0_obs = {
        'cards': player0_cards,
        'win_pile': state['player0_win_pile'],
        'draw_pile': state['player0_draw_pile'],
        'public_revealed_cards': public_revealed_cards
    }
    
    player1_obs = {
        'cards': player1_cards,
        'win_pile': state['player1_win_pile'],
        'draw_pile': state['player1_draw_pile'],
        'public_revealed_cards': public_revealed_cards
    }
    
    return [player0_obs, player1_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # This function would need to implement the logic to stochastically sample a valid sequence of actions
    # For simplicity, we will just return a fixed sequence here
    if player_id == 0:
        return ['play:0', 'play:1', 'play:2', 'play:3', 'play:4', 'play:5', 'play:6', 'play:7', 'play:8', 'play:9', 'play:10', 'play:11', 'play:12', 'play:13', 'play:14', 'play:15']
    else:
        return ['play:0', 'play:1', 'play:2', 'play:3', 'play:4', 'play:5', 'play:6', 'play:7', 'play:8', 'play:9', 'play:10', 'play:11', 'play:12', 'play:13', 'play:14', 'play:15']