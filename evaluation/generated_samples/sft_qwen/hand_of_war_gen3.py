import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper functions
def shuffle_deck(deck):
    """Shuffles the deck."""
    random.shuffle(deck)
    return deck

def deal_cards(deck, num_players):
    """Deals cards evenly between players."""
    return [deck[i::num_players] for i in range(num_players)]

def initialize_game():
    """Initializes the game state."""
    # Standard deck of cards
    deck = ['A', 'K', 'Q', 'J'] * 4
    shuffled_deck = shuffle_deck(deck)
    player1_hand = shuffled_deck[:3]
    player2_hand = shuffled_deck[3:6]
    public_revealed_cards = []
    return {
        'player1_hand': player1_hand,
        'player2_hand': player2_hand,
        'public_revealed_cards': public_revealed_cards,
        'player1_win_pile': [],
        'player2_win_pile': [],
        'current_player': 0,
        'draw_pile': shuffled_deck[6:],
        'terminal_state': False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    if action.startswith('play:'):
        card = action.split(':')[1]
        if state['current_player'] == 0:
            state['player1_hand'].remove(card)
            state['public_revealed_cards'].append(card)
            state['player2_hand'].remove(card)
            state['public_revealed_cards'].append(card)
        else:
            state['player2_hand'].remove(card)
            state['public_revealed_cards'].append(card)
            state['player1_hand'].remove(card)
            state['public_revealed_cards'].append(card)
        if len(state['player1_hand']) < 3:
            state['player1_hand'].extend(state['draw_pile'][:3])
            state['draw_pile'] = state['draw_pile'][3:]
        if len(state['player2_hand']) < 3:
            state['player2_hand'].extend(state['draw_pile'][:3])
            state['draw_pile'] = state['draw_pile'][3:]
        state['current_player'] = 1 if state['current_player'] == 0 else 0
    elif action.startswith('deal:'):
        # This is a chance action, not part of gameplay logic
        pass
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f'Player {player_id}'

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['terminal_state']:
        return [len(state['player1_win_pile']), len(state['player2_win_pile'])]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['terminal_state']:
        return []
    if state['current_player'] == 0:
        return ['play:' + card for card in state['player1_hand']]
    else:
        return ['play:' + card for card in state['player2_hand']]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player1_obs = {
        'hand': state['player1_hand'],
        'win_pile': state['player1_win_pile'],
        'public_revealed_cards': state['public_revealed_cards']
    }
    player2_obs = {
        'hand': state['player2_hand'],
        'win_pile': state['player2_win_pile'],
        'public_revealed_cards': state['public_revealed_cards']
    }
    return [player1_obs, player2_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # For simplicity, we assume deterministic sampling here
    if player_id == 0:
        return ['play:' + obs['hand'][0] for obs in obs_action_history]
    else:
        return ['play:' + obs['hand'][0] for obs in obs_action_history]

# Main game function
def main():
    state = initialize_game()
    while True:
        print(f"Current Player: {get_player_name(get_current_player(state))}")
        print("Player's Hand:", state['player1_hand'] if get_current_player(state) == 0 else state['player2_hand'])
        print("Public Revealed Cards:", state['public_revealed_cards'])
        print("Win Piles:", state['player1_win_pile'], state['player2_win_pile'])
        print("Legal Actions:", get_legal_actions(state))
        action = input("Enter your action (e.g. play:A): ")
        state = apply_action(state, action)
        if get_rewards(state)[0] > 0 or get_rewards(state)[1] > 0:
            print("Game Over!")
            break
        if state['terminal_state']:
            print("Game Over! Final Scores:")
            print(f"Player 1: {len(state['player1_win_pile'])}")
            print(f"Player 2: {len(state['player2_win_pile'])}")
            break

if __name__ == "__main__":
    main()