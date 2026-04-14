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

# Helper function to initialize the game state
def get_initial_state():
    # Initialize the deck and deal cards
    deck = ['A', 'K', 'Q', 'J'] * 4
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
        'current_player': 0
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    if action.startswith('play:'):
        card = action.split(':')[1]
        if card in state['player0_hand']:
            state['player0_hand'].remove(card)
            state['player1_hand'].remove(card)
            state['player0_win_pile'].append(card)
        else:
            state['player1_hand'].remove(card)
            state['player0_hand'].remove(card)
            state['player1_win_pile'].append(card)
    elif action.startswith('deal:'):
        # For simplicity, we assume the dealer deals the entire deck evenly
        # This is a placeholder for actual dealer logic
        pass
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}'

# Get rewards
def get_rewards(state: State) -> list[float]:
    # Rewards are not tracked in this simplified version
    return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> list[Action]:
    player_id = get_current_player(state)
    legal_actions = []
    if player_id == 0:
        legal_actions.append(f'play:{state["player0_hand"][0]}')
        if len(state['player0_hand']) > 1:
            legal_actions.append(f'deal:{state["player0_hand"][1]}')
    else:
        legal_actions.append(f'play:{state["player1_hand"][0]}')
        if len(state['player1_hand']) > 1:
            legal_actions.append(f'deal:{state["player1_hand"][1]}')
    return legal_actions

# Get observations
def get_observations(state: State) -> list[PlayerObservation]:
    player0_obs = {
        'hand': state['player0_hand'],
        'win_pile': state['player0_win_pile']
    }
    player1_obs = {
        'hand': state['player1_hand'],
        'win_pile': state['player1_win_pile']
    }
    return [player0_obs, player1_obs]

# Resample history
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # Placeholder for resampling logic
    # This should ideally sample a valid sequence of actions based on the history
    # For simplicity, we just return a fixed list of actions
    if player_id == 0:
        return ['play:A', 'play:K', 'play:Q', 'play:J']
    else:
        return ['play:J', 'play:Q', 'play:K', 'play:A']

# Main function to run the game
def main():
    state = get_initial_state()
    while True:
        print(f"Current Player: {get_player_name(get_current_player(state))}")
        print("Legal Actions:", get_legal_actions(state))
        action = input("Enter your action (e.g., play:A, deal:KQJ): ")
        state = apply_action(state, action)
        print("New State:")
        print(state)
        obs = get_observations(state)
        print("Observations:")
        print(obs)
        if get_rewards(state)[0] != 0.0 or get_rewards(state)[1] != 0.0:
            break
    print("Game Over!")
    print("Final State:")
    print(state)

if __name__ == "__main__":
    main()