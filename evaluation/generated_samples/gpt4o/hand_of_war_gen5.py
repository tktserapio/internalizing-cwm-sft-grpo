import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple
import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants
RANK_ORDER = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
DECK = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4  # Standard 52-card deck

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = DECK.copy()
    random.shuffle(deck)
    player_0_deck = deck[:26]
    player_1_deck = deck[26:]
    return {
        'player_0_deck': player_0_deck,
        'player_1_deck': player_1_deck,
        'player_0_hand': player_0_deck[:3],
        'player_1_hand': player_1_deck[:3],
        'player_0_win_pile': [],
        'player_1_win_pile': [],
        'publicly_revealed_cards': [],
        'current_player': 0,
        'is_terminal': False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    current_player = new_state['current_player']
    opponent = 1 - current_player
    action_type, card = action.split(':')
    
    if action_type == 'play':
        # Add the played card to the publicly revealed cards
        new_state['publicly_revealed_cards'].append(card)
        
        # Remove the card from the player's hand
        if current_player == 0:
            new_state['player_0_hand'].remove(card)
        else:
            new_state['player_1_hand'].remove(card)
        
        # Check if both players have played
        if len(new_state['publicly_revealed_cards']) == 2:
            # Determine the winner of the battle
            card_0, card_1 = new_state['publicly_revealed_cards']
            rank_0 = RANK_ORDER[card_0]
            rank_1 = RANK_ORDER[card_1]
            
            if rank_0 > rank_1:
                winner = 0
            elif rank_1 > rank_0:
                winner = 1
            else:
                # Handle showdown
                return handle_showdown(new_state)
            
            # Winner takes both cards
            if winner == 0:
                new_state['player_0_win_pile'].extend(new_state['publicly_revealed_cards'])
            else:
                new_state['player_1_win_pile'].extend(new_state['publicly_revealed_cards'])
            
            # Clear the publicly revealed cards
            new_state['publicly_revealed_cards'] = []
            
            # Replenish hands
            replenish_hands(new_state)
        
        # Switch current player
        new_state['current_player'] = opponent
    
    return new_state

def handle_showdown(state: State) -> State:
    """Handles the showdown scenario when cards tie."""
    new_state = state.copy()
    # Burn one card from each player's deck
    if len(new_state['player_0_deck']) > 0 and len(new_state['player_1_deck']) > 0:
        new_state['player_0_deck'].pop(0)
        new_state['player_1_deck'].pop(0)
    
    # Players choose another card to play
    # This will be handled by the next actions taken by players
    
    return new_state

def replenish_hands(state: State):
    """Replenishes players' hands to three cards if possible."""
    if len(state['player_0_deck']) > 0:
        state['player_0_hand'].append(state['player_0_deck'].pop(0))
    if len(state['player_1_deck']) > 0:
        state['player_1_hand'].append(state['player_1_deck'].pop(0))

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['is_terminal']:
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['is_terminal']:
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
    if state['is_terminal']:
        return []
    
    current_player = state['current_player']
    if current_player == 0:
        return [f"play:{card}" for card in state['player_0_hand']]
    else:
        return [f"play:{card}" for card in state['player_1_hand']]

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

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function would require a more complex implementation to accurately reconstruct a valid action sequence
    # based on the observations. For now, we'll return an empty list as a placeholder.
    return []

# Helper function to check if the game has ended
def check_game_end(state: State) -> bool:
    """Checks if the game has ended."""
    if len(state['player_0_deck']) == 0 or len(state['player_1_deck']) == 0:
        state['is_terminal'] = True
        return True
    return False