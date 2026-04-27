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

# Apply action to the state
def apply_action(state: State, action: Action) -> State:
    # Extract the card to play from the action string
    card_to_play = action.split(':')[1]
    
    # Determine the player making the action
    player_id = 0 if state['current_player'] == 0 else 1
    
    # Remove the card from the player's hand
    state[f'{player_id}_hand'].remove(card_to_play)
    
    # Determine the opponent's hand
    opponent_hand = state[f'{1-player_id}_hand']
    
    # Determine the opponent's win pile
    opponent_win_pile = state[f'{1-player_id}_win_pile']
    
    # Determine the publicly revealed cards
    publicly_revealed_cards = state['publicly_revealed_cards']
    
    # Determine the winner of the battle
    if card_to_play > opponent_hand[0]:
        # Player 0 wins
        state[f'{player_id}_win_pile'].append(card_to_play)
        state[f'{player_id}_win_pile'].append(opponent_hand.pop(0))
        state[f'{player_id}_win_pile'].append(opponent_win_pile.pop(0))
        state['current_player'] = 1
    elif card_to_play < opponent_hand[0]:
        # Player 1 wins
        state[f'{player_id}_win_pile'].append(opponent_hand.pop(0))
        state[f'{player_id}_win_pile'].append(card_to_play)
        state[f'{player_id}_win_pile'].append(opponent_win_pile.pop(0))
        state['current_player'] = 0
    else:
        # Showdown
        showdown_cards = [state[f'{player_id}_draw_pile'].pop(0) for _ in range(2)]
        state[f'{player_id}_win_pile'].extend(showdown_cards)
        
        # Determine the winner of the showdown
        if showdown_cards[0] > showdown_cards[1]:
            state[f'{player_id}_win_pile'].append(showdown_cards.pop(0))
            state[f'{player_id}_win_pile'].append(showdown_cards.pop(0))
        else:
            state[f'{player_id}_win_pile'].append(showdown_cards.pop(1))
            state[f'{player_id}_win_pile'].append(showdown_cards.pop(0))
        
        state['current_player'] = 1 if player_id == 0 else 0
    
    # Update the state
    state[f'{player_id}_hand'] = state[f'{player_id}_draw_pile'] + state[f'{player_id}_hand']
    state[f'{1-player_id}_hand'] = state[f'{1-player_id}_draw_pile'] + opponent_hand
    state[f'{1-player_id}_win_pile'] = opponent_win_pile
    
    # Shuffle the draw pile
    state[f'{player_id}_draw_pile'] = state[f'{player_id}_hand'] + state[f'{player_id}_win_pile']
    random.shuffle(state[f'{player_id}_draw_pile'])
    
    # Update the publicly revealed cards
    state['publicly_revealed_cards'] = publicly_revealed_cards + [card_to_play]
    
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}'

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    player0_win_pile = len(state['player0_win_pile'])
    player1_win_pile = len(state['player1_win_pile'])
    
    # Determine the winner based on the win piles
    if player0_win_pile > player1_win_pile:
        return [1.0, 0.0]
    elif player1_win_pile > player0_win_pile:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    legal_actions = []
    player_id = get_current_player(state)
    
    # Check if the game is over
    if len(state[f'{player_id}_hand']) == 0:
        return []
    
    # Generate legal actions
    for card in state[f'{player_id}_hand']:
        legal_actions.append(f'play:{card}')
    
    return legal_actions

# Get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    player0_hand = state['player0_hand']
    player1_hand = state['player1_hand']
    player0_win_pile = state['player0_win_pile']
    player1_win_pile = state['player1_win_pile']
    player0_draw_pile = state['player0_draw_pile']
    player1_draw_pile = state['player1_draw_pile']
    publicly_revealed_cards = state['publicly_revealed_cards']
    
    player0_observation = {
        'hand': player0_hand,
        'win_pile': player0_win_pile,
        'draw_pile': player0_draw_pile,
        'publicly_revealed_cards': publicly_revealed_cards
    }
    
    player1_observation = {
        'hand': player1_hand,
        'win_pile': player1_win_pile,
        'draw_pile': player1_draw_pile,
        'publicly_revealed_cards': publicly_revealed_cards
    }
    
    return [player0_observation, player1_observation]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would need to implement the logic to resample the history
    # For simplicity, we'll just return a fixed sequence of actions
    # This should be replaced with actual resampling logic
    if player_id == 0:
        return ['play:A', 'play:K', 'play:Q']
    else:
        return ['play:J', 'play:K', 'play:A']