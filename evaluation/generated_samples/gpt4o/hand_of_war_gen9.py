import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple, Union

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
RANK_ORDER = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
SUITS = ['H', 'D', 'C', 'S']
DECK = [f"{rank}{suit}" for rank in RANK_ORDER for suit in SUITS]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    random.shuffle(DECK)
    player_0_deck = DECK[:len(DECK)//2]
    player_1_deck = DECK[len(DECK)//2:]
    
    return {
        'player_0_deck': player_0_deck,
        'player_1_deck': player_1_deck,
        'player_0_hand': player_0_deck[:3],
        'player_1_hand': player_1_deck[:3],
        'player_0_win_pile': [],
        'player_1_win_pile': [],
        'publicly_revealed_cards': [],
        'current_player': 0,
        'phase': 'battle'
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    action_type, card = action.split(':')
    
    if action_type == 'play':
        current_player = new_state['current_player']
        hand_key = f'player_{current_player}_hand'
        win_pile_key = f'player_{current_player}_win_pile'
        
        # Remove the card from the player's hand
        new_state[hand_key].remove(card)
        new_state['publicly_revealed_cards'].append(card)
        
        # Check if both players have played their cards
        if len(new_state['publicly_revealed_cards']) == 2:
            # Determine the winner of the battle
            card_0, card_1 = new_state['publicly_revealed_cards']
            winner = determine_battle_winner(card_0, card_1)
            
            if winner is not None:
                # Winner takes both cards
                new_state[f'player_{winner}_win_pile'].extend(new_state['publicly_revealed_cards'])
                new_state['publicly_revealed_cards'] = []
                new_state['phase'] = 'draw'
            else:
                # Showdown occurs
                new_state['phase'] = 'showdown'
        
        # Switch to the next player
        new_state['current_player'] = 1 - current_player
    
    elif action_type == 'deal':
        # Handle dealing cards to players
        pass  # This would be used for initial setup or resampling
    
    return new_state

def determine_battle_winner(card_0: str, card_1: str) -> Union[int, None]:
    """Determine the winner of a battle based on card ranks."""
    rank_0 = RANK_ORDER[card_0[:-1]]
    rank_1 = RANK_ORDER[card_1[:-1]]
    
    if rank_0 > rank_1:
        return 0
    elif rank_1 > rank_0:
        return 1
    else:
        return None

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if is_terminal(state):
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if is_terminal(state):
        player_0_score = len(state['player_0_win_pile'])
        player_1_score = len(state['player_1_win_pile'])
        if player_0_score > player_1_score:
            return [1.0, 0.0]
        elif player_1_score > player_0_score:
            return [0.0, 1.0]
        else:
            return [0.5, 0.5]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if is_terminal(state):
        return []
    
    current_player = state['current_player']
    hand_key = f'player_{current_player}_hand'
    return [f"play:{card}" for card in state[hand_key]]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {
            'hand': state['player_0_hand'],
            'win_pile': state['player_0_win_pile'],
            'publicly_revealed_cards': state['publicly_revealed_cards']
        },
        {
            'hand': state['player_1_hand'],
            'win_pile': state['player_1_win_pile'],
            'publicly_revealed_cards': state['publicly_revealed_cards']
        }
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Union[Action, None]]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions."""
    # This function would require more context on how to resample based on observations
    return []

def is_terminal(state: State) -> bool:
    """Check if the game is in a terminal state."""
    return len(state['player_0_deck']) == 0 or len(state['player_1_deck']) == 0

# Additional helper functions can be defined as needed.