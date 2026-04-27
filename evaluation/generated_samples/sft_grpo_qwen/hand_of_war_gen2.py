import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import List, Dict, Any, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Initial state setup
def get_initial_state() -> State:
    # Shuffle the deck and deal the cards
    deck = ['A', 'K', 'Q', 'J'] * 4  # Assuming a standard deck of 16 cards
    import random
    random.shuffle(deck)
    
    # Deal the deck evenly between two players
    player1_cards = deck[:8]
    player2_cards = deck[8:]
    
    # Form hands
    player1_hand = player1_cards[:3]
    player2_hand = player2_cards[:3]
    
    # Initialize state
    state = {
        'player1_cards': player1_cards,
        'player2_cards': player2_cards,
        'player1_hand': player1_hand,
        'player2_hand': player2_hand,
        'publicly_revealed_cards': [],
        'current_player': 0,
        'player1_win_pile': [],
        'player2_win_pile': [],
        'player1_draw_pile': player1_cards[3:],
        'player2_draw_pile': player2_cards[3:]
    }
    return state

# Apply action to the state
def apply_action(state: State, action: Action) -> State:
    if action.startswith('play:'):
        card_index = int(action.split(':')[1])
        player_id = get_current_player(state)
        
        if player_id == 0:
            player_hand = state['player1_hand']
            player_cards = state['player1_cards']
        else:
            player_hand = state['player2_hand']
            player_cards = state['player2_cards']
        
        if card_index < len(player_hand):
            chosen_card = player_hand[card_index]
            state['publicly_revealed_cards'].append(chosen_card)
            
            if player_id == 0:
                state['player1_hand'][card_index] = 'X'
                state['player1_cards'].remove(chosen_card)
                state['player2_hand'].append(chosen_card)
                state['player2_cards'].remove(chosen_card)
                state['player2_win_pile'].append(chosen_card)
            else:
                state['player2_hand'][card_index] = 'X'
                state['player2_cards'].remove(chosen_card)
                state['player1_hand'].append(chosen_card)
                state['player1_cards'].remove(chosen_card)
                state['player1_win_pile'].append(chosen_card)
                
            state['current_player'] = (state['current_player'] + 1) % 2
            state['player1_draw_pile'].extend(state['player1_cards'])
            state['player2_draw_pile'].extend(state['player2_cards'])
            state['player1_cards'] = []
            state['player2_cards'] = []
            state['player1_hand'] = []
            state['player2_hand'] = []
            
            if state['player1_cards'] == [] and state['player2_cards'] == []:
                state['current_player'] = -4
                
    return state

# Get current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get player name
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}'

# Get rewards
def get_rewards(state: State) -> List[float]:
    player1_win_pile = len(state['player1_win_pile'])
    player2_win_pile = len(state['player2_win_pile'])
    
    if player1_win_pile == 16:
        return [1.0, 0.0]
    elif player2_win_pile == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> List[Action]:
    player_id = get_current_player(state)
    player_hand = state[f'player{player_id}_hand']
    player_cards = state[f'player{player_id}_cards']
    
    if player_cards == [] and player_hand == []:
        return []
    else:
        return [f'play:{i}' for i in range(len(player_hand))]

# Get observations
def get_observations(state: State) -> List[PlayerObservation]:
    player1_hand = state['player1_hand']
    player2_hand = state['player2_hand']
    player1_cards = state['player1_cards']
    player2_cards = state['player2_cards']
    publicly_revealed_cards = state['publicly_revealed_cards']
    
    player1_obs = {
        'hand': player1_hand,
        'cards': player1_cards,
        'revealed_cards': publicly_revealed_cards,
        'opponent_hand': player2_hand,
        'opponent_cards': player2_cards
    }
    
    player2_obs = {
        'hand': player2_hand,
        'cards': player2_cards,
        'revealed_cards': publicly_revealed_cards,
        'opponent_hand': player1_hand,
        'opponent_cards': player1_cards
    }
    
    return [player1_obs, player2_obs]

# Resample history
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Placeholder for resampling logic
    # For simplicity, we will just return a fixed sequence of actions
    # This should be replaced with actual resampling logic
    if player_id == 0:
        return ['play:0', 'play:1', 'play:2', 'play:3', 'play:4', 'play:5', 'play:6', 'play:7']
    else:
        return ['play:0', 'play:1', 'play:2', 'play:3', 'play:4', 'play:5', 'play:6', 'play:7']