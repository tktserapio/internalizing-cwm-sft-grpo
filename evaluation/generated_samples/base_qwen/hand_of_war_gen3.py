import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def initialize_deck() -> List[str]:
    """Initialize the deck with ranks A, K, Q, J."""
    return ['A', 'K', 'Q', 'J'] * 4

def shuffle_deck(deck: List[str]) -> List[str]:
    """Shuffle the deck."""
    random.shuffle(deck)
    return deck

def deal_cards(deck: List[str], num_players: int) -> Tuple[List[str], List[str]]:
    """Deal cards evenly between players."""
    half_deck = len(deck) // num_players
    return (deck[:half_deck], deck[half_deck:])

def draw_card(hand: List[str], draw_pile: List[str]) -> List[str]:
    """Draw a card from the draw pile and add it to the hand."""
    if not draw_pile:
        raise ValueError("Draw pile is empty.")
    drawn_card = draw_pile.pop(0)
    hand.append(drawn_card)
    return hand

def burn_card(draw_pile: List[str]) -> None:
    """Burn a card from the draw pile."""
    if not draw_pile:
        raise ValueError("Draw pile is empty.")
    draw_pile.pop(0)

def declare_showdown(hand: List[str], draw_pile: List[str]) -> List[str]:
    """Declare a showdown and return the winning card."""
    if not draw_pile:
        raise ValueError("Draw pile is empty.")
    burned_card = draw_pile.pop(0)
    chosen_card = hand.pop(0)
    return chosen_card

# Game functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = initialize_deck()
    shuffled_deck = shuffle_deck(deck)
    player0_hand, player1_hand = deal_cards(shuffled_deck, 2)
    player0_draw_pile, player1_draw_pile = shuffled_deck[:len(player0_hand)], shuffled_deck[len(player0_hand):]
    return {
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'player0_draw_pile': player0_draw_pile,
        'player1_draw_pile': player1_draw_pile,
        'player0_win_pile': [],
        'player1_win_pile': [],
        'current_player': 0
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    if action.startswith('play:'):
        card_index = int(action.split(':')[1])
        if card_index < len(state['player0_hand']):
            player_id = 0
        else:
            player_id = 1
            card_index -= len(state['player0_hand'])
        state[player_id + '_hand'].pop(card_index)
        state[player_id + '_win_pile'].append(action)
    elif action.startswith('deal:'):
        # Implement dealing cards logic here
        pass
    else:
        raise ValueError(f"Invalid action: {action}")
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['player0_win_pile'] == ['A', 'K', 'Q', 'J'] * 4:
        return -4
    if state['player1_win_pile'] == ['A', 'K', 'Q', 'J'] * 4:
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['current_player'] == -4:
        return [1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['current_player'] == -4:
        return []
    player_id = state['current_player']
    legal_actions = []
    if player_id == 0:
        legal_actions.extend(['play:' + str(i) for i in range(len(state['player0_hand']))])
    else:
        legal_actions.extend(['play:' + str(i + len(state['player0_hand'])) for i in range(len(state['player1_hand']))])
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player0_obs = {
        'hand': state['player0_hand'],
        'draw_pile': state['player0_draw_pile'],
        'win_pile': state['player0_win_pile']
    }
    player1_obs = {
        'hand': state['player1_hand'],
        'draw_pile': state['player1_draw_pile'],
        'win_pile': state['player1_win_pile']
    }
    return [player0_obs, player1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    return obs_action_history[-1][1].split(',') if obs_action_history else []

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print(initial_state)
    
    # Apply some actions
    actions = [
        'play:0',
        'play:1',
        'play:2',
        'play:3',
        'play:4',
        'play:5'
    ]
    for action in actions:
        initial_state = apply_action(initial_state, action)
        print(initial_state)