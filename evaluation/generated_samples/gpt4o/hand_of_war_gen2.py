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
SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
DECK = [f"{rank}" for rank in RANKS for _ in SUITS]  # Simplified deck without suits for simplicity

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Shuffle the deck and deal to both players
    random.shuffle(DECK)
    player_0_draw_pile = DECK[:len(DECK)//2]
    player_1_draw_pile = DECK[len(DECK)//2:]
    
    # Initial state setup
    state = {
        'draw_piles': [player_0_draw_pile, player_1_draw_pile],
        'hands': [player_0_draw_pile[:3], player_1_draw_pile[:3]],
        'win_piles': [[], []],
        'current_player': 0,
        'publicly_revealed_cards': [],
        'phase': 'battle',  # can be 'battle' or 'showdown'
        'showdown_cards': [None, None]
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
    new_state['draw_piles'] = [pile.copy() for pile in state['draw_piles']]
    new_state['publicly_revealed_cards'] = state['publicly_revealed_cards'][:]
    
    player = new_state['current_player']
    opponent = 1 - player
    
    if action.startswith("play:"):
        card = action.split(":")[1]
        new_state['hands'][player].remove(card)
        new_state['publicly_revealed_cards'].append(card)
        
        if new_state['phase'] == 'battle':
            if len(new_state['publicly_revealed_cards']) == 2:
                # Resolve battle
                card_0, card_1 = new_state['publicly_revealed_cards']
                winner = resolve_battle(card_0, card_1)
                if winner is not None:
                    new_state['win_piles'][winner].extend(new_state['publicly_revealed_cards'])
                    new_state['publicly_revealed_cards'] = []
                else:
                    new_state['phase'] = 'showdown'
                new_state['current_player'] = 0
            else:
                new_state['current_player'] = opponent
        elif new_state['phase'] == 'showdown':
            if new_state['showdown_cards'][player] is None:
                new_state['showdown_cards'][player] = card
                if all(new_state['showdown_cards']):
                    showdown_winner = resolve_battle(*new_state['showdown_cards'])
                    if showdown_winner is not None:
                        new_state['win_piles'][showdown_winner].extend(new_state['publicly_revealed_cards'] + new_state['showdown_cards'])
                        new_state['publicly_revealed_cards'] = []
                        new_state['showdown_cards'] = [None, None]
                        new_state['phase'] = 'battle'
                    else:
                        # Another showdown
                        new_state['publicly_revealed_cards'].extend(new_state['showdown_cards'])
                        new_state['showdown_cards'] = [None, None]
                    new_state['current_player'] = 0
                else:
                    new_state['current_player'] = opponent

    # Replenish hands
    for i in range(2):
        while len(new_state['hands'][i]) < 3 and new_state['draw_piles'][i]:
            new_state['hands'][i].append(new_state['draw_piles'][i].pop(0))
    
    return new_state

def resolve_battle(card_0: str, card_1: str) -> int:
    """Determines the winner of a battle. Returns 0, 1, or None for tie."""
    rank_0 = RANKS.index(card_0)
    rank_1 = RANKS.index(card_1)
    if rank_0 > rank_1:
        return 0
    elif rank_1 > rank_0:
        return 1
    return None

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
        win_pile_counts = [len(pile) for pile in state['win_piles']]
        if win_pile_counts[0] > win_pile_counts[1]:
            return [1.0, 0.0]
        elif win_pile_counts[1] > win_pile_counts[0]:
            return [0.0, 1.0]
        return [0.5, 0.5]  # Draw
    return [0.0, 0.0]

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
            'publicly_revealed_cards': state['publicly_revealed_cards'],
            'draw_pile_count': len(state['draw_piles'][0])
        },
        {
            'hand': state['hands'][1],
            'win_pile': state['win_piles'][1],
            'publicly_revealed_cards': state['publicly_revealed_cards'],
            'draw_pile_count': len(state['draw_piles'][1])
        }
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function is complex and requires a deep understanding of the game mechanics and history.
    # For simplicity, this implementation is a placeholder and should be replaced with a proper stochastic sampling.
    return [action for _, action in obs_action_history if action is not None]

def is_terminal(state: State) -> bool:
    """Determines if the game is in a terminal state."""
    return any(len(draw_pile) == 0 for draw_pile in state['draw_piles']) or any(len(win_pile) == 16 for win_pile in state['win_piles'])