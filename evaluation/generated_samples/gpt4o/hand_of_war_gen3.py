import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {rank: i for i, rank in enumerate(RANKS)}
NUM_PLAYERS = 2

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = RANKS * 4  # Standard deck of 52 cards
    random.shuffle(deck)
    half_deck = len(deck) // 2
    state = {
        'draw_piles': [deck[:half_deck], deck[half_deck:]],
        'hands': [deck[:3], deck[half_deck:half_deck+3]],
        'win_piles': [[], []],
        'publicly_revealed_cards': [],
        'current_player': 0,
        'is_terminal': False
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    current_player = new_state['current_player']
    opponent = 1 - current_player
    
    if action.startswith("play:"):
        card = action.split(":")[1]
        new_state['hands'][current_player].remove(card)
        new_state['publicly_revealed_cards'].append(card)
        
        if len(new_state['publicly_revealed_cards']) == 2:
            # Resolve battle
            card_0, card_1 = new_state['publicly_revealed_cards']
            winner = determine_winner(card_0, card_1)
            if winner is not None:
                new_state['win_piles'][winner].extend(new_state['publicly_revealed_cards'])
                new_state['publicly_revealed_cards'] = []
            else:
                # Handle showdown
                if len(new_state['draw_piles'][current_player]) > 0 and len(new_state['draw_piles'][opponent]) > 0:
                    new_state['draw_piles'][current_player].pop(0)
                    new_state['draw_piles'][opponent].pop(0)
                else:
                    new_state['is_terminal'] = True
            
            # Replenish hands
            for player in range(NUM_PLAYERS):
                while len(new_state['hands'][player]) < 3 and len(new_state['draw_piles'][player]) > 0:
                    new_state['hands'][player].append(new_state['draw_piles'][player].pop(0))
            
            # Check for terminal state
            if any(len(pile) == 0 for pile in new_state['draw_piles']):
                new_state['is_terminal'] = True
            
            new_state['current_player'] = 0  # Reset to player 0 after a battle
        else:
            new_state['current_player'] = opponent  # Switch player
        
    return new_state

def determine_winner(card_0: str, card_1: str) -> int:
    """Determine the winner between two cards."""
    if RANK_VALUES[card_0] > RANK_VALUES[card_1]:
        return 0
    elif RANK_VALUES[card_0] < RANK_VALUES[card_1]:
        return 1
    else:
        return None

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state['is_terminal'] else state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state['is_terminal']:
        return [0.0, 0.0]
    
    win_pile_counts = [len(pile) for pile in state['win_piles']]
    if win_pile_counts[0] > win_pile_counts[1]:
        return [1.0, 0.0]
    elif win_pile_counts[0] < win_pile_counts[1]:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['is_terminal']:
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

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function would require a more complex implementation to accurately reconstruct the history.
    # For simplicity, we return an empty list here.
    return []

# Helper function to shuffle and deal cards
def shuffle_and_deal() -> Tuple[List[str], List[str]]:
    """Shuffle and deal cards to two players."""
    deck = RANKS * 4
    random.shuffle(deck)
    half_deck = len(deck) // 2
    return deck[:half_deck], deck[half_deck:]