import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the state
def get_initial_state() -> State:
    # Initialize the deck and deal the cards
    deck = ['A', 'K', 'Q', 'J'] * 4  # 16 cards total
    random.shuffle(deck)
    
    # Shuffle and deal the deck evenly between two players
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
        card = action.split(':')[1]
        if card in state['player0_hand']:
            state['player0_hand'].remove(card)
            state['player0_win_pile'].append(card)
        else:
            state['player1_hand'].remove(card)
            state['player1_win_pile'].append(card)
    elif action.startswith('deal:'):
        # For now, we don't need to implement the deal action since it's not part of the gameplay logic
        pass
    
    # Update the current player
    state['current_player'] = (state['current_player'] + 1) % 2
    
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
    
    if player0_win_pile == 16:
        return [1.0, 0.0]
    elif player1_win_pile == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    current_player = get_current_player(state)
    player_hand = state[f'player{current_player}_hand']
    player_win_pile = state[f'player{current_player}_win_pile']
    
    if player_hand:
        return [f'play:{card}' for card in player_hand]
    else:
        return []

# Get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    player0_obs = {
        'hand': state['player0_hand'],
        'win_pile': state['player0_win_pile'],
        'draw_pile': state['player0_draw_pile']
    }
    player1_obs = {
        'hand': state['player1_hand'],
        'win_pile': state['player1_win_pile'],
        'draw_pile': state['player1_draw_pile']
    }
    
    return [player0_obs, player1_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # For simplicity, we assume that the history is deterministic and just return the last action
    if obs_action_history:
        return [obs_action_history[-1][1]]
    else:
        return []

# Example usage
if __name__ == "__main__":
    state = get_initial_state()
    print("Initial State:", state)
    
    # Simulate a few rounds of the game
    for _ in range(5):
        legal_actions = get_legal_actions(state)
        print(f"Legal Actions: {legal_actions}")
        
        # Player 0 plays a card
        action = random.choice(legal_actions)
        state = apply_action(state, action)
        print(f"Applied Action: {action}, Current State: {state}")
        
        # Switch to Player 1
        state['current_player'] = (state['current_player'] + 1) % 2
        
    print("Final State:", state)