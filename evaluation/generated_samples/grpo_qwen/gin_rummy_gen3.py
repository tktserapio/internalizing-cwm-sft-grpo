import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Dict, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to generate a shuffled deck
def shuffle_deck() -> List[int]:
    suits = ['S', 'C', 'D', 'H']
    ranks = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A']
    deck = [(rank + suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

# Initial state of the game
def get_initial_state() -> State:
    # Initialize the deck
    deck = shuffle_deck()
    # Shuffle the deck to create a new stock pile
    stock_pile = deck[:]
    # Deal half of the deck to each player
    player1_hand = deck[:26]
    player2_hand = deck[26:]
    # Determine the dealer
    dealer = random.choice([0, 1])
    # Determine the knock card
    knock_card = random.randint(1, 10)
    # Set up the state
    state = {
        'deck': deck,
        'stock_pile': stock_pile,
        'dealer': dealer,
        'knock_card': knock_card,
        'player1_hand': player1_hand,
        'player2_hand': player2_hand,
        'current_player': dealer,
        'phase': 'Draw',
        'player1_deadwood': 0,
        'player2_deadwood': 0,
        'player1_melds': [],
        'player2_melds': []
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['stock_pile'].append(new_state['deck'].pop())
        new_state['phase'] = 'Discard'
    elif action.startswith('Action: '):
        card_to_discard = action[7:]
        if card_to_discard in new_state['player1_hand']:
            new_state['player1_hand'].remove(card_to_discard)
            new_state['player1_deadwood'] += new_state['deck'].pop().value
            new_state['phase'] = 'Knock'
        else:
            raise ValueError(f"Card {card_to_discard} not in player1_hand")
    elif action == 'Knock':
        new_state['phase'] = 'Layoff'
        new_state['player1_melds'], new_state['player2_melds'], new_state['player1_deadwood'], new_state['player2_deadwood'] = lay_off(new_state)
    elif action == 'Done':
        new_state['phase'] = 'Wall'
    elif action == 'Pass':
        new_state['phase'] = 'Wall'
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

# Determine the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    if state['phase'] == 'Wall':
        return [0.0, 0.0]
    else:
        return [state['player1_deadwood'], state['player2_deadwood']]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    elif state['phase'] == 'Knock':
        return ['Action: ' + card for card in state['player1_hand']]
    elif state['phase'] == 'Layoff':
        return ['Action: ' + card for card in state['player1_hand']] + ['Done']
    elif state['phase'] == 'Wall':
        return []

# Get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    player1_obs = {
        'deadwood': state['player1_deadwood'],
        'melds': state['player1_melds'],
        'hand': state['player1_hand']
    }
    player2_obs = {
        'deadwood': state['player2_deadwood'],
        'melds': state['player2_melds'],
        'hand': state['player2_hand']
    }
    return [player1_obs, player2_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    if len(obs_action_history) == 0:
        return []
    elif obs_action_history[-1][1] is None:
        return resample_history(obs_action_history[:-1], player_id)
    else:
        return [obs_action_history[-1][1]]

# Function to lay off the hand
def lay_off(state: State) -> tuple[List[List[int]], List[List[int]], int, int]:
    player1_melds = []
    player2_melds = []
    player1_deadwood = 0
    player2_deadwood = 0
    for card in state['player1_hand']:
        if card in state['player2_hand']:
            state['player2_hand'].remove(card)
            state['player2_deadwood'] += state['deck'].pop().value
            player2_melds.append([card])
            player2_deadwood += state['deck'].pop().value
        else:
            player1_melds.append([card])
            player1_deadwood += state['deck'].pop().value
    return player1_melds, player2_melds, player1_deadwood, player2_deadwood

# Main function to simulate the game
def main():
    state = get_initial_state()
    while True:
        print(f"Current State: {state}")
        player_id = get_current_player(state)
        print(f"Player {player_id}'s turn.")
        legal_actions = get_legal_actions(state)
        print(f"Legal Actions: {legal_actions}")
        action = input("Choose an action: ")
        try:
            state = apply_action(state, action)
            print(f"New State: {state}")
            if state['phase'] == 'Wall':
                print("Game Over!")
                break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()