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

# Constants for card ranks
CARD_RANKS = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
REVERSE_CARD_RANKS = {v: k for k, v in CARD_RANKS.items()}

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = list(CARD_RANKS.keys()) * 2  # Two sets of cards
    random.shuffle(deck)
    player_0_deck = deck[:16]
    player_1_deck = deck[16:]
    state = {
        'draw_piles': [player_0_deck, player_1_deck],
        'hands': [player_0_deck[:3], player_1_deck[:3]],
        'win_piles': [[], []],
        'current_player': 0,
        'publicly_revealed_cards': [],
        'showdown': False
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

    if action.startswith("play:"):
        card = action.split(":")[1]
        player = state['current_player']
        opponent = 1 - player
        new_state['publicly_revealed_cards'].append((player, card))
        new_state['hands'][player].remove(card)

        if len(new_state['publicly_revealed_cards']) == 2:
            card_0, card_1 = new_state['publicly_revealed_cards']
            rank_0 = CARD_RANKS[card_0[1]]
            rank_1 = CARD_RANKS[card_1[1]]

            if rank_0 > rank_1:
                new_state['win_piles'][0].extend([card_0[1], card_1[1]])
            elif rank_1 > rank_0:
                new_state['win_piles'][1].extend([card_0[1], card_1[1]])
            else:
                new_state['showdown'] = True

            new_state['publicly_revealed_cards'] = []

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
    if not is_terminal(state):
        return [0.0, 0.0]
    player_0_score = len(state['win_piles'][0])
    player_1_score = len(state['win_piles'][1])
    if player_0_score > player_1_score:
        return [1.0, 0.0]
    elif player_1_score > player_0_score:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if is_terminal(state):
        return []
    player = state['current_player']
    return [f"play:{card}" for card in state['hands'][player]]

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
    # This function would require more context about the game history and randomness to implement correctly.
    # For now, we return an empty list, as this is non-trivial without additional information.
    return []

def is_terminal(state: State) -> bool:
    """Check if the game is in a terminal state."""
    for player in range(2):
        if len(state['draw_piles'][player]) == 0 and len(state['hands'][player]) == 0:
            return True
    return False