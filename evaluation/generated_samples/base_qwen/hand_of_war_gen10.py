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
    player0_hand = deck[:3]
    player1_hand = deck[3:6]
    player0_win_pile = []
    player1_win_pile = []
    player0_draw_pile = deck[6:]
    player1_draw_pile = deck[6:]
    
    return {
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'player0_win_pile': player0_win_pile,
        'player1_win_pile': player1_win_pile,
        'player0_draw_pile': player0_draw_pile,
        'player1_draw_pile': player1_draw_pile,
        'current_player': 0,
        'publicly_revealed_cards': [],
        'game_over': False
    }

# Apply an action to the game state
def apply_action(state: State, action: Action) -> State:
    if action.startswith('play:'):
        card_index = int(action.split(':')[1])
        current_player = state['current_player']
        if current_player == 0:
            state['player0_hand'][card_index], state['player1_hand'][card_index] = state['player1_hand'][card_index], state['player0_hand'][card_index]
        else:
            state['player1_hand'][card_index], state['player0_hand'][card_index] = state['player0_hand'][card_index], state['player1_hand'][card_index]
        state['publicly_revealed_cards'].append(action)
        state['current_player'] = (state['current_player'] + 1) % 2
        return state
    elif action.startswith('deal:'):
        # For simplicity, we assume the dealer deals cards evenly and doesn't need to be implemented here
        return state
    else:
        raise ValueError("Invalid action")

# Determine the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards for the players
def get_rewards(state: State) -> list[float]:
    # Rewards are not tracked in this simplified version
    return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    current_player = state['current_player']
    player_hand = state[f'player{current_player}_hand']
    publicly_revealed_cards = state['publicly_revealed_cards']
    possible_actions = []
    
    for card in player_hand:
        if card not in publicly_revealed_cards:
            possible_actions.append(f'play:{player_hand.index(card)}')
    
    return possible_actions

# Get the observations for the players
def get_observations(state: State) -> list[PlayerObservation]:
    player0_hand = state['player0_hand']
    player1_hand = state['player1_hand']
    player0_win_pile = state['player0_win_pile']
    player1_win_pile = state['player1_win_pile']
    player0_draw_pile = state['player0_draw_pile']
    player1_draw_pile = state['player1_draw_pile']
    
    return [
        {
            'hand': player0_hand,
            'win_pile': player0_win_pile,
            'draw_pile': player0_draw_pile
        },
        {
            'hand': player1_hand,
            'win_pile': player1_win_pile,
            'draw_pile': player1_draw_pile
        }
    ]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # This function would typically involve sampling from the possible actions based on the history
    # For simplicity, we just return a fixed sequence of actions
    if player_id == 0:
        return ['play:0', 'play:1', 'play:2', 'play:3', 'play:4', 'play:5', 'play:6', 'play:7', 'play:8', 'play:9', 'play:10', 'play:11', 'play:12', 'play:13', 'play:14', 'play:15']
    else:
        return ['play:0', 'play:1', 'play:2', 'play:3', 'play:4', 'play:5', 'play:6', 'play:7', 'play:8', 'play:9', 'play:10', 'play:11', 'play:12', 'play:13', 'play:14', 'play:15']

# Main function to run the game
def main():
    state = get_initial_state()
    print("Initial State:", state)
    
    while True:
        current_player = get_current_player(state)
        print(f"Current Player: {get_player_name(current_player)}")
        
        legal_actions = get_legal_actions(state)
        print(f"Legal Actions: {legal_actions}")
        
        observation = get_observations(state)
        print(f"Observations: {observation}")
        
        # Simulate a move by the player
        action = random.choice(legal_actions)
        print(f"Action: {action}")
        
        state = apply_action(state, action)
        print("New State:", state)
        
        if get_rewards(state):
            print("Rewards:", get_rewards(state))
            break
    
    print("Game Over!")

if __name__ == "__main__":
    main()