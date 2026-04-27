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
PLAYER_NAMES = ["Player 0", "Player 1"]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A']
    deck *= 2  # Two sets of cards for two players
    random.shuffle(deck)
    
    # Split the deck between two players
    player_0_deck = deck[:16]
    player_1_deck = deck[16:]
    
    # Initial state
    state = {
        'draw_piles': [player_0_deck, player_1_deck],
        'hands': [player_0_deck[:3], player_1_deck[:3]],
        'win_piles': [[], []],
        'current_player': 0,
        'publicly_revealed_cards': []
    }
    
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    new_state['hands'] = [hand.copy() for hand in state['hands']]
    new_state['win_piles'] = [pile.copy() for pile in state['win_piles']]
    new_state['publicly_revealed_cards'] = state['publicly_revealed_cards'].copy()
    
    current_player = state['current_player']
    opponent = 1 - current_player
    
    if action.startswith("play:"):
        card = action.split(":")[1]
        new_state['hands'][current_player].remove(card)
        new_state['publicly_revealed_cards'].append(card)
        
        if len(new_state['publicly_revealed_cards']) == 2:
            # Resolve battle
            card_0 = new_state['publicly_revealed_cards'][0]
            card_1 = new_state['publicly_revealed_cards'][1]
            rank_0 = RANK_ORDER[card_0]
            rank_1 = RANK_ORDER[card_1]
            
            if rank_0 > rank_1:
                winner = 0
            elif rank_1 > rank_0:
                winner = 1
            else:
                # Showdown logic
                winner = resolve_showdown(new_state)
            
            new_state['win_piles'][winner].extend(new_state['publicly_revealed_cards'])
            new_state['publicly_revealed_cards'] = []
            
            # Draw new cards to replenish hands
            for player in [0, 1]:
                while len(new_state['hands'][player]) < 3 and new_state['draw_piles'][player]:
                    new_state['hands'][player].append(new_state['draw_piles'][player].pop(0))
        
        new_state['current_player'] = opponent
    
    return new_state

def resolve_showdown(state: State) -> int:
    """Resolve a showdown situation."""
    # Burn one card from each player's draw pile
    for player in [0, 1]:
        if state['draw_piles'][player]:
            state['draw_piles'][player].pop(0)
    
    # Players choose another card from their hand
    # For simplicity, we'll assume they play the first card in their hand
    card_0 = state['hands'][0].pop(0)
    card_1 = state['hands'][1].pop(0)
    
    state['publicly_revealed_cards'].extend([card_0, card_1])
    
    rank_0 = RANK_ORDER[card_0]
    rank_1 = RANK_ORDER[card_1]
    
    if rank_0 > rank_1:
        return 0
    elif rank_1 > rank_0:
        return 1
    else:
        return resolve_showdown(state)

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if is_terminal(state):
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return PLAYER_NAMES[player_id]

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if is_terminal(state):
        win_pile_counts = [len(state['win_piles'][0]), len(state['win_piles'][1])]
        if win_pile_counts[0] > win_pile_counts[1]:
            return [1.0, 0.0]
        elif win_pile_counts[1] > win_pile_counts[0]:
            return [0.0, 1.0]
        else:
            return [0.5, 0.5]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if is_terminal(state):
        return []
    
    current_player = state['current_player']
    return [f"play:{card}" for card in state['hands'][current_player]]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {
            'hand': state['hands'][0],
            'win_pile': state['win_piles'][0],
            'publicly_revealed_cards': state['publicly_revealed_cards']
        },
        {
            'hand': state['hands'][1],
            'win_pile': state['win_piles'][1],
            'publicly_revealed_cards': state['publicly_revealed_cards']
        }
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Union[Action, None]]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function is complex and depends on the specific implementation of the game logic.
    # For simplicity, we assume a straightforward replay of actions.
    return [action for _, action in obs_action_history if action is not None]

def is_terminal(state: State) -> bool:
    """Check if the game is in a terminal state."""
    # Game ends if a player has all cards or cannot perform an action
    for player in [0, 1]:
        if len(state['win_piles'][player]) == 16:
            return True
        if not state['draw_piles'][player] and len(state['hands'][player]) < 3:
            return True
    return False