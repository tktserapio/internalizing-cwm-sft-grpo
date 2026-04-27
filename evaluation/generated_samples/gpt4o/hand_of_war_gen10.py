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

# Constants
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {rank: i for i, rank in enumerate(RANKS)}
NUM_PLAYERS = 2

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = RANKS * 4
    random.shuffle(deck)
    player_hands = [deck[:len(deck)//2], deck[len(deck)//2:]]
    return {
        'player_hands': player_hands,
        'player_win_piles': [[], []],
        'player_current_hands': [player_hands[0][:3], player_hands[1][:3]],
        'publicly_revealed_cards': [],
        'current_player': 0,
        'game_over': False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player = new_state['current_player']
    opponent = 1 - player
    
    if action.startswith("play:"):
        card = action.split(":")[1]
        new_state['publicly_revealed_cards'].append(card)
        new_state['player_current_hands'][player].remove(card)
        
        # Check if both players have played
        if len(new_state['publicly_revealed_cards']) == 2:
            card1, card2 = new_state['publicly_revealed_cards']
            if RANK_VALUES[card1] > RANK_VALUES[card2]:
                winner = 0
            elif RANK_VALUES[card1] < RANK_VALUES[card2]:
                winner = 1
            else:
                # Handle Showdown
                winner = handle_showdown(new_state)
            
            # Add cards to winner's win pile
            new_state['player_win_piles'][winner].extend(new_state['publicly_revealed_cards'])
            new_state['publicly_revealed_cards'] = []
            
            # Replenish hands
            for p in range(NUM_PLAYERS):
                while len(new_state['player_current_hands'][p]) < 3 and new_state['player_hands'][p]:
                    new_state['player_current_hands'][p].append(new_state['player_hands'][p].pop(0))
            
            # Check for game over conditions
            if not new_state['player_hands'][player] and len(new_state['player_current_hands'][player]) < 3:
                new_state['game_over'] = True
            
            # Switch current player
            new_state['current_player'] = opponent
    
    return new_state

def handle_showdown(state: State) -> int:
    """Handles the showdown scenario and returns the winner."""
    # Burn one card from each player's draw pile
    for p in range(NUM_PLAYERS):
        if state['player_hands'][p]:
            state['player_hands'][p].pop(0)
    
    # Players choose another card from their hand
    # For simplicity, assume players always choose the first card in hand
    card1 = state['player_current_hands'][0][0]
    card2 = state['player_current_hands'][1][0]
    
    if RANK_VALUES[card1] > RANK_VALUES[card2]:
        return 0
    elif RANK_VALUES[card1] < RANK_VALUES[card2]:
        return 1
    else:
        # Recursive showdown
        return handle_showdown(state)

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state['game_over'] else state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state['game_over']:
        return [0.0, 0.0]
    
    win_pile_counts = [len(state['player_win_piles'][p]) for p in range(NUM_PLAYERS)]
    if win_pile_counts[0] > win_pile_counts[1]:
        return [1.0, 0.0]
    elif win_pile_counts[0] < win_pile_counts[1]:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['game_over']:
        return []
    
    current_player = state['current_player']
    return [f"play:{card}" for card in state['player_current_hands'][current_player]]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {
            'hand': state['player_current_hands'][0],
            'win_pile': state['player_win_piles'][0],
            'publicly_revealed_cards': state['publicly_revealed_cards']
        },
        {
            'hand': state['player_current_hands'][1],
            'win_pile': state['player_win_piles'][1],
            'publicly_revealed_cards': state['publicly_revealed_cards']
        }
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function would involve complex logic to reconstruct the history based on observations.
    # For simplicity, we return an empty list as a placeholder.
    return []