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

# Helper functions
def parse_deck(deck: List[str]) -> List[str]:
    """Parses the deck into a shuffled list of cards."""
    return sorted(deck, key=lambda x: x == 'A', reverse=True)

def get_initial_state(deck: List[str]) -> State:
    """Returns the initial game state before any actions are taken."""
    # Shuffle the deck
    shuffled_deck = parse_deck(deck)
    
    # Deal the deck evenly between two players
    player1_cards = shuffled_deck[:8]
    player2_cards = shuffled_deck[8:]
    
    # Form hands
    player1_hand = player1_cards[:3]
    player2_hand = player2_cards[:3]
    
    # Initialize state
    state = {
        'deck': deck,
        'player1_cards': player1_cards,
        'player2_cards': player2_cards,
        'player1_hand': player1_hand,
        'player2_hand': player2_hand,
        'public_revealed_cards': [],
        'current_player': 0,
        'player1_win_pile': [],
        'player2_win_pile': []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    
    if action.startswith('play:'):
        card_value = action.split(':')[1]
        if card_value in new_state['player1_hand']:
            new_state['player1_hand'].remove(card_value)
            new_state['player1_win_pile'].append(card_value)
        else:
            new_state['player2_hand'].remove(card_value)
            new_state['player2_win_pile'].append(card_value)
    elif action.startswith('deal:'):
        # For simplicity, we assume the deck is already shuffled and dealt
        pass
    
    # Update public revealed cards
    new_state['public_revealed_cards'].append(action)
    
    # Switch current player
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f'Player {player_id}'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    player1_win_pile = len(state['player1_win_pile'])
    player2_win_pile = len(state['player2_win_pile'])
    
    if player1_win_pile == 16:
        return [1.0, 0.0]
    elif player2_win_pile == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = get_current_player(state)
    player1_hand = state['player1_hand']
    player2_hand = state['player2_hand']
    
    if current_player == 0:
        return ['play:' + card for card in player1_hand]
    else:
        return ['play:' + card for card in player2_hand]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player1_hand = state['player1_hand']
    player2_hand = state['player2_hand']
    player1_win_pile = state['player1_win_pile']
    player2_win_pile = state['player2_win_pile']
    
    player1_obs = {
        'hand': player1_hand,
        'win_pile': player1_win_pile
    }
    player2_obs = {
        'hand': player2_hand,
        'win_pile': player2_win_pile
    }
    
    return [player1_obs, player2_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we just return a fixed sequence of actions
    if player_id == 0:
        return ['play:A', 'play:K', 'play:Q', 'play:J']
    else:
        return ['play:A', 'play:K', 'play:Q', 'play:J']