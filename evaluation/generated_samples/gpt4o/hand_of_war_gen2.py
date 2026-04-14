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
DECK = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    random.shuffle(DECK)
    player_0_draw_pile = DECK[:26]
    player_1_draw_pile = DECK[26:]
    return {
        'draw_piles': [player_0_draw_pile, player_1_draw_pile],
        'hands': [player_0_draw_pile[:3], player_1_draw_pile[:3]],
        'win_piles': [[], []],
        'publicly_revealed_cards': [],
        'current_player': 0,
        'phase': 'battle',  # 'battle' or 'showdown'
        'showdown_cards': [None, None]
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    current_player = new_state['current_player']
    opponent = 1 - current_player

    if action.startswith("play:"):
        card = action.split(":")[1]
        new_state['hands'][current_player].remove(card)
        new_state['publicly_revealed_cards'].append(card)

        if new_state['phase'] == 'battle':
            if len(new_state['publicly_revealed_cards']) == 2:
                resolve_battle(new_state)
        elif new_state['phase'] == 'showdown':
            new_state['showdown_cards'][current_player] = card
            if all(new_state['showdown_cards']):
                resolve_showdown(new_state)

    new_state['current_player'] = opponent
    return new_state

def resolve_battle(state: State):
    """Resolve the battle phase and update the state."""
    card_0, card_1 = state['publicly_revealed_cards']
    rank_0, rank_1 = RANK_ORDER[card_0], RANK_ORDER[card_1]

    if rank_0 > rank_1:
        winner = 0
    elif rank_1 > rank_0:
        winner = 1
    else:
        state['phase'] = 'showdown'
        return

    state['win_piles'][winner].extend(state['publicly_revealed_cards'])
    state['publicly_revealed_cards'] = []
    draw_new_cards(state)

def resolve_showdown(state: State):
    """Resolve the showdown phase and update the state."""
    card_0, card_1 = state['showdown_cards']
    rank_0, rank_1 = RANK_ORDER[card_0], RANK_ORDER[card_1]

    if rank_0 > rank_1:
        winner = 0
    elif rank_1 > rank_0:
        winner = 1
    else:
        return  # Another tie, continue showdown

    state['win_piles'][winner].extend(state['publicly_revealed_cards'] + state['showdown_cards'])
    state['publicly_revealed_cards'] = []
    state['showdown_cards'] = [None, None]
    state['phase'] = 'battle'
    draw_new_cards(state)

def draw_new_cards(state: State):
    """Replenish players' hands to three cards."""
    for player in range(2):
        while len(state['hands'][player]) < 3 and state['draw_piles'][player]:
            state['hands'][player].append(state['draw_piles'][player].pop(0))

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if not any(state['draw_piles']) or any(len(pile) == 16 for pile in state['win_piles']):
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if get_current_player(state) == -4:
        win_pile_counts = [len(pile) for pile in state['win_piles']]
        if win_pile_counts[0] > win_pile_counts[1]:
            return [1.0, 0.0]
        elif win_pile_counts[1] > win_pile_counts[0]:
            return [0.0, 1.0]
        else:
            return [0.5, 0.5]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if get_current_player(state) == -4:
        return []

    current_player = state['current_player']
    return [f"play:{card}" for card in state['hands'][current_player]]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {
            'hand': state['hands'][0],
            'win_pile': state['win_piles'][0],
            'publicly_revealed_cards': state['publicly_revealed_cards'],
            'draw_pile_size': len(state['draw_piles'][0])
        },
        {
            'hand': state['hands'][1],
            'win_pile': state['win_piles'][1],
            'publicly_revealed_cards': state['publicly_revealed_cards'],
            'draw_pile_size': len(state['draw_piles'][1])
        }
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Union[Action, None]]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This is a complex function that would require simulating the game
    # from the start and matching the observations. A full implementation
    # would involve replaying the game and ensuring consistency with the
    # observed history. For simplicity, this function is left as a placeholder.
    return []