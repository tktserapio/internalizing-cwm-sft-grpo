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
    deck = ['A', 'K', 'Q', 'J'] * 4  # 16 cards in total
    shuffled_deck = deck[:]  # Shuffle the deck
    np.random.shuffle(shuffled_deck)
    
    # Deal the deck evenly between two players
    player0_hand = shuffled_deck[:8]
    player1_hand = shuffled_deck[8:]
    
    # Form hands
    player0_draw_pile = shuffled_deck[8:]
    player1_draw_pile = shuffled_deck[:8]
    
    # Initialize state
    state = {
        'deck': shuffled_deck,
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'player0_draw_pile': player0_draw_pile,
        'player1_draw_pile': player1_draw_pile,
        'player0_win_pile': [],
        'player1_win_pile': [],
        'current_player': 0,
        'publicly_revealed_cards': []
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Ensure the action is valid
    if action.startswith('play:') and len(action.split(':')) == 2:
        card = action.split(':')[1]
        if card in state['player0_hand']:
            state['player0_hand'].remove(card)
            state['player0_win_pile'].append(card)
        else:
            state['player1_hand'].remove(card)
            state['player1_win_pile'].append(card)
    elif action.startswith('deal:'):
        # Implement deal action if needed
        pass
    else:
        raise ValueError("Invalid action")
    
    # Update current player
    state['current_player'] = (state['current_player'] + 1) % 2
    
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards
def get_rewards(state: State) -> List[float]:
    # Calculate rewards based on win piles
    player0_win_pile = len(state['player0_win_pile'])
    player1_win_pile = len(state['player1_win_pile'])
    
    if player0_win_pile == 16:
        return [1.0, 0.0]
    elif player1_win_pile == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> List[Action]:
    legal_actions = []
    if state['current_player'] == 0:
        legal_actions.extend(['play:' + card for card in state['player0_hand']])
    else:
        legal_actions.extend(['play:' + card for card in state['player1_hand']])
    
    return legal_actions

# Get observations
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

# Resample history
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would need to implement the logic to resample actions given the history
    # For simplicity, we will just return a random action from the legal actions
    legal_actions = get_legal_actions(resample_history.get_initial_state())
    return [legal_actions[np.random.randint(len(legal_actions))]]