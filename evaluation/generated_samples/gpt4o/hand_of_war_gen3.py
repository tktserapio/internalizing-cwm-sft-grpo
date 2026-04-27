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
NUM_CARDS_PER_PLAYER = 16
HAND_SIZE = 3

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = RANKS * 4
    random.shuffle(deck)
    
    player_0_deck = deck[:NUM_CARDS_PER_PLAYER]
    player_1_deck = deck[NUM_CARDS_PER_PLAYER:]
    
    return {
        'player_0_deck': player_0_deck,
        'player_1_deck': player_1_deck,
        'player_0_hand': player_0_deck[:HAND_SIZE],
        'player_1_hand': player_1_deck[:HAND_SIZE],
        'player_0_win_pile': [],
        'player_1_win_pile': [],
        'publicly_revealed_cards': [],
        'current_player': 0,
        'phase': 'battle'
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    action_type, card = action.split(':')
    
    if action_type == 'play':
        current_player = new_state['current_player']
        opponent = 1 - current_player
        hand_key = f'player_{current_player}_hand'
        win_pile_key = f'player_{current_player}_win_pile'
        opponent_hand_key = f'player_{opponent}_hand'
        opponent_win_pile_key = f'player_{opponent}_win_pile'
        
        # Remove the played card from the player's hand
        new_state[hand_key].remove(card)
        new_state['publicly_revealed_cards'].append(card)
        
        # Check if both players have played their cards
        if len(new_state['publicly_revealed_cards']) == 2:
            # Determine the winner of the battle
            card_0, card_1 = new_state['publicly_revealed_cards']
            if RANK_VALUES[card_0] > RANK_VALUES[card_1]:
                new_state[win_pile_key].extend(new_state['publicly_revealed_cards'])
            elif RANK_VALUES[card_0] < RANK_VALUES[card_1]:
                new_state[opponent_win_pile_key].extend(new_state['publicly_revealed_cards'])
            else:
                # Handle showdown
                new_state['phase'] = 'showdown'
            
            # Clear the publicly revealed cards
            new_state['publicly_revealed_cards'] = []
            
            # Replenish hands
            replenish_hand(new_state, current_player)
            replenish_hand(new_state, opponent)
        
        # Switch players
        new_state['current_player'] = opponent
    
    return new_state

def replenish_hand(state: State, player: int):
    """Replenishes the player's hand to the hand size."""
    hand_key = f'player_{player}_hand'
    deck_key = f'player_{player}_deck'
    
    while len(state[hand_key]) < HAND_SIZE and state[deck_key]:
        state[hand_key].append(state[deck_key].pop(0))

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
    
    player_0_score = len(state['player_0_win_pile'])
    player_1_score = len(state['player_1_win_pile'])
    
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
    
    current_player = state['current_player']
    hand_key = f'player_{current_player}_hand'
    return [f'play:{card}' for card in state[hand_key]]

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
    # This function would require more context about the history and how to resample it.
    # For simplicity, we'll assume a simple replay of actions.
    actions = []
    for obs, action in obs_action_history:
        if action is not None:
            actions.append(action)
    return actions

def is_terminal(state: State) -> bool:
    """Checks if the game is in a terminal state."""
    return (
        len(state['player_0_deck']) == 0 and len(state['player_0_hand']) == 0 or
        len(state['player_1_deck']) == 0 and len(state['player_1_hand']) == 0 or
        len(state['player_0_win_pile']) == 32 or
        len(state['player_1_win_pile']) == 32
    )