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
def get_initial_state() -> State:
    # Initialize the deck and deal cards
    deck = ['A', 'K', 'Q', 'J'] * 4  # 16 cards total
    random.shuffle(deck)
    
    # Shuffle and deal the deck evenly
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

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    if action.startswith('play:'):
        card_index = int(action.split(':')[1])
        player_id = get_current_player(state)
        
        # Remove the chosen card from the hand
        state[f'player{player_id}_hand'][card_index] = state[f'player{player_id}_draw_pile'].pop()
        
        # Determine the winner of the battle
        if player_id == 0:
            opponent_id = 1
        else:
            opponent_id = 0
        
        # Get the opponent's card
        opponent_card = state[f'player{opponent_id}_hand'][0]
        state[f'publicly_revealed_cards'].append(opponent_card)
        
        # Determine the winner
        if state[f'player{player_id}_hand'][0] > opponent_card:
            state['player0_win_pile'].extend(state[f'publicly_revealed_cards'])
            state[f'player{player_id}_win_pile'].append(state[f'player{player_id}_hand'][0])
            state[f'player{player_id}_hand'].pop(0)
            state[f'player{opponent_id}_hand'].pop(0)
        elif state[f'player{player_id}_hand'][0] < opponent_card:
            state['player1_win_pile'].extend(state[f'publicly_revealed_cards'])
            state[f'player{player_id}_win_pile'].append(state[f'player{player_id}_hand'][0])
            state[f'player{player_id}_hand'].pop(0)
            state[f'player{opponent_id}_hand'].pop(0)
        else:
            # Showdown
            state['showdown'] = True
            state['player0_showdown_card'] = state[f'player{player_id}_hand'][0]
            state['player1_showdown_card'] = state[f'player{opponent_id}_hand'][0]
            
            while state['showdown']:
                state['player0_showdown_card'] = state[f'player{player_id}_draw_pile'].pop()
                state['player1_showdown_card'] = state[f'player{opponent_id}_draw_pile'].pop()
                
                if state['player0_showdown_card'] > state['player1_showdown_card']:
                    state['player0_win_pile'].extend(state[f'publicly_revealed_cards'])
                    state[f'player{player_id}_win_pile'].append(state['player0_showdown_card'])
                    state[f'player{player_id}_hand'].append(state['player0_showdown_card'])
                    state[f'player{player_id}_hand'].append(state['player1_showdown_card'])
                    state[f'player{opponent_id}_hand'].append(state['player1_showdown_card'])
                    break
                elif state['player0_showdown_card'] < state['player1_showdown_card']:
                    state['player1_win_pile'].extend(state[f'publicly_revealed_cards'])
                    state[f'player{player_id}_win_pile'].append(state['player1_showdown_card'])
                    state[f'player{player_id}_hand'].append(state['player0_showdown_card'])
                    state[f'player{player_id}_hand'].append(state['player1_showdown_card'])
                    state[f'player{opponent_id}_hand'].append(state['player0_showdown_card'])
                    break
                else:
                    state['showdown'] = False
    
    return state

# Determine the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get rewards
def get_rewards(state: State) -> list[float]:
    player0_win_pile = len(state['player0_win_pile'])
    player1_win_pile = len(state['player1_win_pile'])
    
    if player0_win_pile == 16:
        return [1.0, 0.0]
    elif player1_win_pile == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> list[Action]:
    player_id = get_current_player(state)
    player_hand = state[f'player{player_id}_hand']
    public_revealed_cards = state['publicly_revealed_cards']
    
    if player_hand:
        return [f'play:{i}' for i in range(len(player_hand))]
    else:
        return []

# Get observations
def get_observations(state: State) -> list[PlayerObservation]:
    player0_hand = state['player0_hand']
    player1_hand = state['player1_hand']
    player0_win_pile = state['player0_win_pile']
    player1_win_pile = state['player1_win_pile']
    player0_draw_pile = state['player0_draw_pile']
    player1_draw_pile = state['player1_draw_pile']
    publicly_revealed_cards = state['publicly_revealed_cards']
    
    player0_obs = {
        'hand': player0_hand,
        'win_pile': player0_win_pile,
        'draw_pile': player0_draw_pile,
        'publicly_revealed_cards': publicly_revealed_cards
    }
    
    player1_obs = {
        'hand': player1_hand,
        'win_pile': player1_win_pile,
        'draw_pile': player1_draw_pile,
        'publicly_revealed_cards': publicly_revealed_cards
    }
    
    return [player0_obs, player1_obs]

# Resample history
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    state = get_initial_state()
    for obs, action in obs_action_history:
        state = apply_action(state, action)
    
    # Determine the current player based on the last action
    last_action = obs_action_history[-1][1]
    if last_action is None:
        return []
    elif last_action.startswith('play:'):
        player_id = 0 if last_action.split(':')[1] == '0' else 1
    
    # Generate a random sequence of actions
    actions = []
    while True:
        if state['current_player'] == player_id:
            actions.append(random.choice(get_legal_actions(state)))
        else:
            actions.append(None)
        
        if get_current_player(state) != player_id:
            break
    
    return actions