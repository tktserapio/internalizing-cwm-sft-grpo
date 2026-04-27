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
def create_deck():
    ranks = ['A', 'K', 'Q', 'J']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    return [{'rank': rank, 'suit': suit} for suit in suits for rank in ranks]

# Initial state function
def get_initial_state():
    # Create a deck of cards
    deck = create_deck()
    random.shuffle(deck)
    
    # Shuffle and deal the deck evenly between two players
    player0_cards = deck[:8]
    player1_cards = deck[8:]
    
    # Form hands
    player0_hand = [deck[0], deck[1], deck[2]]
    player1_hand = [deck[3], deck[4], deck[5]]
    
    # Initialize state
    state = {
        'player0_cards': player0_cards,
        'player1_cards': player1_cards,
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'publicly_revealed_cards': [],
        'player0_win_pile': [],
        'player1_win_pile': [],
        'current_player': 0,
        'draw_pile': deck[8:],
        'showdown_count': 0,
        'showdown_winner': None,
        'showdown_burn': None,
        'showdown_cards': []
    }
    return state

# Apply action function
def apply_action(state: State, action: Action) -> State:
    if action.startswith('play:'):
        card_value = action.split(':')[1]
        player_id = state['current_player']
        
        # Remove the played card from the player's hand
        state[f'player{player_id}_hand'].remove(card_value)
        
        # Add the played card to the win pile of the current player
        state[f'player{player_id}_win_pile'].append(card_value)
        
        # Determine the winner of the battle
        if player_id == 0:
            opponent_id = 1
        else:
            opponent_id = 0
        
        opponent_card = state[f'player{opponent_id}_hand'][0]
        if card_value > opponent_card:
            # Player 0 wins
            state[f'player0_win_pile'].append(opponent_card)
            state[f'player1_win_pile'].append(card_value)
        elif card_value < opponent_card:
            # Player 1 wins
            state[f'player1_win_pile'].append(opponent_card)
            state[f'player0_win_pile'].append(card_value)
        else:
            # Showdown occurs
            state['showdown_count'] += 1
            state['showdown_winner'] = None
            state['showdown_burn'] = None
            state['showdown_cards'] = [card_value, opponent_card]
            
            while state['showdown_winner'] is None:
                # Player 0 plays a card from their draw pile
                state[f'player0_draw_pile'].pop(0)
                state[f'player0_hand'].append(state[f'player0_draw_pile'][0])
                
                # Player 1 plays a card from their draw pile
                state[f'player1_draw_pile'].pop(0)
                state[f'player1_hand'].append(state[f'player1_draw_pile'][0])
                
                # Choose battle cards
                state['showdown_cards'].extend([state[f'player0_hand'][0], state[f'player1_hand'][0]])
                
                # Determine showdown winner
                if state['showdown_cards'][0] > state['showdown_cards'][1]:
                    state['showdown_winner'] = 0
                else:
                    state['showdown_winner'] = 1
                
                # Burn a card
                if state['showdown_winner'] == 0:
                    state[f'player0_draw_pile'].pop(0)
                else:
                    state[f'player1_draw_pile'].pop(0)
                
                # Remove the drawn cards from the hands
                state[f'player0_hand'].remove(state[f'player0_hand'][0])
                state[f'player1_hand'].remove(state[f'player1_hand'][0])
                
                # Add the won cards to the respective win piles
                if state['showdown_winner'] == 0:
                    state[f'player0_win_pile'].append(state['showdown_cards'][0])
                    state[f'player1_win_pile'].append(state['showdown_cards'][1])
                else:
                    state[f'player1_win_pile'].append(state['showdown_cards'][0])
                    state[f'player0_win_pile'].append(state['showdown_cards'][1])
                
                # Update the current player
                state['current_player'] = (state['current_player'] + 1) % 2
    
    # Update the publicly revealed cards
    state['publicly_revealed_cards'].append(action)
    
    return state

# Get current player function
def get_current_player(state: State) -> int:
    return state['current_player']

# Get player name function
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}'

# Get rewards function
def get_rewards(state: State) -> List[float]:
    player0_win_pile = len(state['player0_win_pile'])
    player1_win_pile = len(state['player1_win_pile'])
    
    # Check if the game is over
    if player0_win_pile == 16 or player1_win_pile == 16:
        return [1.0, 0.0] if player0_win_pile == 16 else [0.0, 1.0]
    elif player0_win_pile > player1_win_pile:
        return [1.0, 0.0]
    elif player1_win_pile > player0_win_pile:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

# Get legal actions function
def get_legal_actions(state: State) -> List[Action]:
    player_id = get_current_player(state)
    player_hand = state[f'player{player_id}_hand']
    player_win_pile = state[f'player{player_id}_win_pile']
    player_draw_pile = state[f'player{player_id}_draw_pile']
    
    # Check if the game is over
    if len(player_hand) == 0:
        return []
    
    legal_actions = []
    
    # Play a card from the hand
    for card in player_hand:
        legal_actions.append(f'play:{card}')
    
    # Draw a card from the draw pile
    if len(player_draw_pile) > 0:
        legal_actions.append('deal:')
        for card in player_draw_pile:
            legal_actions.append(f'{card},')
    
    return legal_actions

# Get observations function
def get_observations(state: State) -> List[PlayerObservation]:
    player0_hand = state[f'player0_hand']
    player1_hand = state[f'player1_hand']
    player0_win_pile = state[f'player0_win_pile']
    player1_win_pile = state[f'player1_win_pile']
    player0_draw_pile = state[f'player0_draw_pile']
    player1_draw_pile = state[f'player1_draw_pile']
    
    player0_observation = {
        'hand': player0_hand,
        'win_pile': player0_win_pile,
        'draw_pile': player0_draw_pile,
        'publicly_revealed_cards': state['publicly_revealed_cards'],
        'showdown_count': state['showdown_count'],
        'showdown_winner': state['showdown_winner'],
        'showdown_burn': state['showdown_burn'],
        'showdown_cards': state['showdown_cards']
    }
    
    player1_observation = {
        'hand': player1_hand,
        'win_pile': player1_win_pile,
        'draw_pile': player1_draw_pile,
        'publicly_revealed_cards': state['publicly_revealed_cards'],
        'showdown_count': state['showdown_count'],
        'showdown_winner': state['showdown_winner'],
        'showdown_burn': state['showdown_burn'],
        'showdown_cards': state['showdown_cards']
    }
    
    return [player0_observation, player1_observation]

# Resample history function
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would need to implement the logic to resample a valid sequence of actions
    # based on the given observations. For simplicity, we will just return a dummy list here.
    return ['play:7', 'play:K', 'play:A']