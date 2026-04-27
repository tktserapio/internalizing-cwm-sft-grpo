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
    # Initialize the deck
    deck = ['A', 'K', 'Q', 'J'] * 4
    
    # Shuffle the deck
    random.shuffle(deck)
    
    # Deal the deck evenly between two players
    player1_cards = deck[:8]
    player2_cards = deck[8:]
    
    # Form hands
    player1_hand = player1_cards[:3]
    player2_hand = player2_cards[:3]
    
    # Create the state dictionary
    state = {
        'deck': deck,
        'player1_cards': player1_cards,
        'player2_cards': player2_cards,
        'player1_hand': player1_hand,
        'player2_hand': player2_hand,
        'publicly_revealed_cards': [],
        'player1_win_pile': [],
        'player2_win_pile': [],
        'player1_draw_pile': player1_cards[3:],
        'player2_draw_pile': player2_cards[3:],
        'current_player': 0,
        'player1_score': 0,
        'player2_score': 0
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    if action.startswith('play:'):
        player_id = get_current_player(state)
        card_to_play = action.split(':')[1]
        
        if player_id == 0:
            player_hand = state['player1_hand']
            player_cards = state['player1_cards']
        else:
            player_hand = state['player2_hand']
            player_cards = state['player2_cards']
        
        if card_to_play in player_hand:
            player_hand.remove(card_to_play)
            player_cards.remove(card_to_play)
            
            # Determine the winner of the battle
            opponent_card = random.choice([state['player1_hand'][0], state['player2_hand'][0]])
            if card_to_play > opponent_card:
                # Player wins the battle
                state['player1_win_pile'].append(card_to_play)
                state['player1_win_pile'].append(opponent_card)
                state['player1_draw_pile'].extend(state['publicly_revealed_cards'])
                state['publicly_revealed_cards'] = []
            else:
                # Opponent wins the battle
                state['player2_win_pile'].append(card_to_play)
                state['player2_win_pile'].append(opponent_card)
                state['player2_draw_pile'].extend(state['publicly_revealed_cards'])
                state['publicly_revealed_cards'] = []
                
            # Draw new cards
            if len(state['player1_draw_pile']) < 3:
                state['player1_draw_pile'].extend(state['player1_cards'][-3:])
            if len(state['player2_draw_pile']) < 3:
                state['player2_draw_pile'].extend(state['player2_cards'][-3:])
            
            state['current_player'] = 1 if player_id == 0 else 0
        else:
            raise ValueError("Invalid card played.")
    else:
        raise ValueError("Invalid action format.")
    
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    return [len(state['player1_win_pile']), len(state['player2_win_pile'])]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    player_id = get_current_player(state)
    player_hand = state[f'player{player_id}_hand']
    player_cards = state[f'player{player_id}_cards']
    publicly_revealed_cards = state['publicly_revealed_cards']
    
    # Check if the draw pile is empty
    if len(state[f'player{player_id}_draw_pile']) == 0:
        return []
    
    # Check if the player can play a card
    if len(player_hand) > 0:
        return [f'play:{card}' for card in player_hand]
    
    # Check if the player can burn a card during a showdown
    if len(publicly_revealed_cards) > 0:
        return [f'deal:{card}' for card in player_hand] + [f'play:{card}' for card in player_hand]
    
    return []

# Get the observations for the current state
def get_observations(state: State) -> list[PlayerObservation]:
    player1_obs = {
        'win_pile': state['player1_win_pile'],
        'draw_pile': state['player1_draw_pile'],
        'score': len(state['player1_win_pile']),
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    player2_obs = {
        'win_pile': state['player2_win_pile'],
        'draw_pile': state['player2_draw_pile'],
        'score': len(state['player2_win_pile']),
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    return [player1_obs, player2_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # This function would need to be implemented based on the specific game logic and observation history.
    # For simplicity, we will just return a fixed sequence of actions.
    # In a real implementation, this function would be stochastic and based on the observed history.
    if player_id == 0:
        return ['play:A', 'play:K', 'play:Q', 'play:J']
    else:
        return ['play:J', 'play:Q', 'play:K', 'play:A']