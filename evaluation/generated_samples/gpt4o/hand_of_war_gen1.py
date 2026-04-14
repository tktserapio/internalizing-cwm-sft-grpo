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
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {rank: i for i, rank in enumerate(RANKS)}
NUM_CARDS = 16

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = RANKS * 4  # Assuming a standard deck of cards
    random.shuffle(deck)
    player_0_deck = deck[:NUM_CARDS]
    player_1_deck = deck[NUM_CARDS:2*NUM_CARDS]
    return {
        'draw_piles': [player_0_deck, player_1_deck],
        'hands': [player_0_deck[:3], player_1_deck[:3]],
        'win_piles': [[], []],
        'publicly_revealed_cards': [],
        'current_player': 0,
        'terminal': False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    new_state['hands'] = [hand.copy() for hand in state['hands']]
    new_state['win_piles'] = [pile.copy() for pile in state['win_piles']]
    new_state['publicly_revealed_cards'] = state['publicly_revealed_cards'].copy()
    
    if action.startswith("play:"):
        card = action.split(":")[1]
        current_player = state['current_player']
        opponent = 1 - current_player
        
        # Remove the played card from the player's hand
        new_state['hands'][current_player].remove(card)
        new_state['publicly_revealed_cards'].append(card)
        
        # Check if both players have played
        if len(new_state['publicly_revealed_cards']) == 2:
            # Determine the winner of the battle
            card_0, card_1 = new_state['publicly_revealed_cards']
            value_0, value_1 = RANK_VALUES[card_0], RANK_VALUES[card_1]
            
            if value_0 > value_1:
                winner = 0
            elif value_1 > value_0:
                winner = 1
            else:
                # Handle Showdown
                winner = handle_showdown(new_state)
            
            if winner is not None:
                new_state['win_piles'][winner].extend(new_state['publicly_revealed_cards'])
                new_state['publicly_revealed_cards'] = []
            
            # Replenish hands
            for player in range(2):
                while len(new_state['hands'][player]) < 3 and new_state['draw_piles'][player]:
                    new_state['hands'][player].append(new_state['draw_piles'][player].pop(0))
            
            # Check for game end condition
            if not new_state['draw_piles'][0] or not new_state['draw_piles'][1]:
                new_state['terminal'] = True
                new_state['current_player'] = -4
            else:
                new_state['current_player'] = 1 - current_player
        else:
            new_state['current_player'] = 1 - current_player
    
    return new_state

def handle_showdown(state: State) -> Union[int, None]:
    """Handles the showdown scenario and returns the winner if determined."""
    # Burn one card from each player's draw pile
    for player in range(2):
        if state['draw_piles'][player]:
            state['draw_piles'][player].pop(0)
        else:
            return 1 - player  # Opponent wins if a player cannot burn
    
    # Both players play another card
    return None  # Continue the showdown

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state['terminal']:
        return [0.0, 0.0]
    
    win_counts = [len(state['win_piles'][0]), len(state['win_piles'][1])]
    if win_counts[0] > win_counts[1]:
        return [1.0, 0.0]
    elif win_counts[1] > win_counts[0]:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['terminal']:
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
    # This function would require a more complex implementation to properly resample the history
    # based on the observations and actions. For simplicity, we will return an empty list here.
    return []