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
SUITS = ['H', 'D', 'C', 'S']  # Hearts, Diamonds, Clubs, Spades
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
DECK = [rank + suit for suit in SUITS for rank in RANKS]
RANK_VALUES = {rank: i for i, rank in enumerate(RANKS, start=2)}

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = DECK[:]
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
        'phase': 'battle',  # or 'showdown'
        'showdown_cards': []
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    player = new_state['current_player']
    opponent = 1 - player
    
    if action.startswith("play:"):
        card = action.split(":")[1]
        new_state['publicly_revealed_cards'].append(card)
        new_state[f'player_{player}_hand'].remove(card)
        
        if len(new_state['publicly_revealed_cards']) == 2:
            # Resolve battle or showdown
            card_0, card_1 = new_state['publicly_revealed_cards']
            winner = determine_winner(card_0, card_1)
            if winner is not None:
                # Winner takes both cards
                new_state[f'player_{winner}_win_pile'].extend(new_state['publicly_revealed_cards'])
                new_state['publicly_revealed_cards'] = []
                new_state['phase'] = 'battle'
            else:
                # Tie, initiate showdown
                new_state['phase'] = 'showdown'
                new_state['showdown_cards'] = new_state['publicly_revealed_cards']
                new_state['publicly_revealed_cards'] = []
        
        # Replenish hand
        draw_card(new_state, player)
        
        # Switch player
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

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # This is a complex function that would require a detailed implementation
    # based on the specific rules of the game and the observation history.
    # For simplicity, this is left as a placeholder.
    return []

def determine_winner(card_0: str, card_1: str) -> int | None:
    """Determines the winner between two cards, or None if it's a tie."""
    rank_0 = RANK_VALUES[card_0[:-1]]
    rank_1 = RANK_VALUES[card_1[:-1]]
    
    if rank_0 > rank_1:
        return 0
    elif rank_1 > rank_0:
        return 1
    else:
        return None

def draw_card(state: State, player: int) -> None:
    """Replenishes the player's hand to three cards if possible."""
    draw_pile = state[f'player_{player}_deck']
    hand = state[f'player_{player}_hand']
    
    while len(hand) < 3 and draw_pile:
        hand.append(draw_pile.pop(0))

def is_terminal(state: State) -> bool:
    """Checks if the game is in a terminal state."""
    player_0_deck_empty = not state['player_0_deck'] and len(state['player_0_hand']) < 3
    player_1_deck_empty = not state['player_1_deck'] and len(state['player_1_hand']) < 3
    
    return player_0_deck_empty or player_1_deck_empty

# Note: The resample_history function is left as a placeholder as it requires a more complex implementation.