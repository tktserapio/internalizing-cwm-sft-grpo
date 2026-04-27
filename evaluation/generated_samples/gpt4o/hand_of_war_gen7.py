import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants for card ranks
CARD_RANKS = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
RANK_ORDER = list(CARD_RANKS.keys())

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = RANK_ORDER * 4  # Full deck of 52 cards
    random.shuffle(deck)
    player_0_deck = deck[:26]
    player_1_deck = deck[26:]
    
    return {
        'draw_pile': [player_0_deck, player_1_deck],
        'hand': [player_0_deck[:3], player_1_deck[:3]],
        'win_pile': [[], []],
        'publicly_revealed_cards': [],
        'current_player': 0,
        'terminal': False
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    new_state['publicly_revealed_cards'] = state['publicly_revealed_cards'][:]
    
    if action.startswith("play:"):
        card = action.split(":")[1]
        player = new_state['current_player']
        opponent = 1 - player
        
        # Remove the card from the player's hand
        new_state['hand'][player].remove(card)
        
        # Add to publicly revealed cards
        new_state['publicly_revealed_cards'].append((player, card))
        
        # If both players have played, resolve the battle
        if len(new_state['publicly_revealed_cards']) == 2:
            resolve_battle(new_state)
        
        # Switch player
        new_state['current_player'] = opponent
    
    return new_state

def resolve_battle(state: State):
    """Resolves the battle between two played cards."""
    player_0_card = state['publicly_revealed_cards'][0][1]
    player_1_card = state['publicly_revealed_cards'][1][1]
    
    if CARD_RANKS[player_0_card] > CARD_RANKS[player_1_card]:
        winner = 0
    elif CARD_RANKS[player_0_card] < CARD_RANKS[player_1_card]:
        winner = 1
    else:
        winner = None  # Tie, initiate showdown
    
    if winner is not None:
        # Winner takes both cards
        state['win_pile'][winner].extend([player_0_card, player_1_card])
        state['publicly_revealed_cards'].clear()
    else:
        # Handle showdown
        handle_showdown(state)

def handle_showdown(state: State):
    """Handles the showdown scenario when cards tie."""
    # Each player places a card face down
    for player in range(2):
        if state['draw_pile'][player]:
            state['draw_pile'][player].pop(0)  # Burn a card

    # Players play another card from their hand
    # This will be handled in the next round of play actions

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player'] if not state['terminal'] else -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['terminal']:
        player_0_score = len(state['win_pile'][0])
        player_1_score = len(state['win_pile'][1])
        if player_0_score > player_1_score:
            return [1.0, 0.0]
        elif player_0_score < player_1_score:
            return [0.0, 1.0]
        else:
            return [0.5, 0.5]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['terminal']:
        return []
    
    player = state['current_player']
    return [f"play:{card}" for card in state['hand'][player]]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {
            'hand': state['hand'][0],
            'win_pile': state['win_pile'][0],
            'publicly_revealed_cards': state['publicly_revealed_cards']
        },
        {
            'hand': state['hand'][1],
            'win_pile': state['win_pile'][1],
            'publicly_revealed_cards': state['publicly_revealed_cards']
        }
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function is complex and requires a detailed understanding of the game history and stochastic elements.
    # For simplicity, this implementation is a placeholder and should be expanded based on game requirements.
    return [action for _, action in obs_action_history if action is not None]

# Note: Additional helper functions may be required to handle specific game logic, such as replenishing hands, checking for terminal states, etc.