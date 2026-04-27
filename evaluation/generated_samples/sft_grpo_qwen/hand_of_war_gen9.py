import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import List, Dict, Any, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def parse_deck(deck: List[int]) -> List[int]:
    """Converts a shuffled deck of cards into a list of integers representing ranks."""
    return sorted(deck, reverse=True)

def convert_card_value(card: int) -> str:
    """Converts a card value to its corresponding string representation."""
    card_values = {14: 'A', 13: 'K', 12: 'Q', 11: 'J'}
    return card_values.get(card, str(card))

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initialize the deck and deal it evenly between two players
    deck = list(range(1, 15)) * 2  # Shuffled deck
    player0_cards = parse_deck(deck[:8])
    player1_cards = parse_deck(deck[8:])
    
    return {
        'deck': deck,
        'player0_cards': player0_cards,
        'player1_cards': player1_cards,
        'player0_draw_pile': player0_cards,
        'player1_draw_pile': player1_cards,
        'player0_win_pile': [],
        'player1_win_pile': [],
        'current_player': 0,
        'publicly_revealed_cards': []
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    if action.startswith('play:'):
        card_index = int(action.split(':')[1])
        card = state['player0_cards'][card_index]
        state['player0_cards'].pop(card_index)
        state['publicly_revealed_cards'].append(card)
        
        if state['current_player'] == 0:
            state['player0_cards'].append(card)
        else:
            state['player1_cards'].append(card)
        
        state['current_player'] = (state['current_player'] + 1) % 2
        
        if len(state['player0_cards']) == 0 or len(state['player1_cards']) == 0:
            state['publicly_revealed_cards'] = []
            state['current_player'] = -4  # Terminal state
    
    elif action.startswith('deal:'):
        cards_to_deal = action.split(':')[1].split(',')
        state['player0_draw_pile'] += cards_to_deal
        state['player1_draw_pile'] += cards_to_deal
        state['player0_cards'] = parse_deck(state['player0_draw_pile'])
        state['player1_cards'] = parse_deck(state['player1_draw_pile'])
    
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f'Player {player_id}'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['current_player'] == -4:
        return [len(state['player0_win_pile']), len(state['player1_win_pile'])]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['current_player'] == -4:
        return []
    
    if state['player0_cards']:
        return ['play:' + str(i) for i in range(len(state['player0_cards']))]
    if state['player1_cards']:
        return ['play:' + str(i) for i in range(len(state['player1_cards']))]
    
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player0_obs = {
        'deck': state['deck'],
        'draw_pile': state['player0_draw_pile'],
        'win_pile': state['player0_win_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    player1_obs = {
        'deck': state['deck'],
        'draw_pile': state['player1_draw_pile'],
        'win_pile': state['player1_win_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    return [player0_obs, player1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we will just return a fixed sequence of actions
    if player_id == 0:
        return ['play:0', 'play:1', 'play:2', 'play:3', 'play:4', 'play:5', 'play:6', 'play:7', 'play:8', 'play:9', 'play:10', 'play:11', 'play:12', 'play:13', 'play:14']
    else:
        return ['play:0', 'play:1', 'play:2', 'play:3', 'play:4', 'play:5', 'play:6', 'play:7', 'play:8', 'play:9', 'play:10', 'play:11', 'play:12', 'play:13', 'play:14']