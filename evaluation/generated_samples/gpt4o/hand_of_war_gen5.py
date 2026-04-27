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
CARD_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
CARD_VALUES = {rank: i for i, rank in enumerate(CARD_RANKS, start=2)}

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = CARD_RANKS * 4  # Standard deck of 52 cards
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
        'round': 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    new_state['round'] += 1
    player = state['current_player']
    opponent = 1 - player

    if action.startswith("play:"):
        card_played = action.split(":")[1]
        new_state[f'player_{player}_hand'].remove(card_played)
        new_state['publicly_revealed_cards'].append(card_played)

        if len(new_state['publicly_revealed_cards']) == 2:
            # Resolve the battle
            card_0 = new_state['publicly_revealed_cards'][0]
            card_1 = new_state['publicly_revealed_cards'][1]
            value_0 = CARD_VALUES[card_0]
            value_1 = CARD_VALUES[card_1]

            if value_0 > value_1:
                new_state['player_0_win_pile'].extend(new_state['publicly_revealed_cards'])
            elif value_1 > value_0:
                new_state['player_1_win_pile'].extend(new_state['publicly_revealed_cards'])
            else:
                # Handle showdown
                pass  # Showdown logic to be implemented

            new_state['publicly_revealed_cards'] = []
            new_state['current_player'] = 0  # Reset to player 0

        else:
            new_state['current_player'] = opponent

    return new_state

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
    hand = state[f'player_{current_player}_hand']
    return [f"play:{card}" for card in hand]

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
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function would require a more complex implementation to simulate the game history
    # based on observations. For simplicity, we return an empty list here.
    return []

def is_terminal(state: State) -> bool:
    """Determine if the game is in a terminal state."""
    return len(state['player_0_deck']) == 0 or len(state['player_1_deck']) == 0

# Additional helper functions can be added here to handle specific game logic, such as showdowns.