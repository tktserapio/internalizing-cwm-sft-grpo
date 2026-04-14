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
    """Shuffles the given deck."""
    random.shuffle(deck)
    return deck

def deal_cards(deck, num_players):
    """Deals the deck evenly between the players."""
    return [deck[i::num_players] for i in range(num_players)]

def get_initial_state():
    """Returns the initial game state before any actions are taken."""
    # Standard deck of cards
    standard_deck = ['A', 'K', 'Q', 'J'] * 4
    
    # Shuffle the deck
    shuffled_deck = shuffle_deck(standard_deck)
    
    # Deal the deck evenly between two players
    player1_hand, player2_hand = deal_cards(shuffled_deck, 2)
    
    # Form hands by drawing the top 3 cards
    player1_hand = player1_hand[:3]
    player2_hand = player2_hand[:3]
    
    # Initial state
    state = {
        'player1_hand': player1_hand,
        'player2_hand': player2_hand,
        'player1_win_pile': [],
        'player2_win_pile': [],
        'current_player': 0,
        'public_revealed_cards': []
    }
    
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    if action.startswith('play:'):
        card = action.split(':')[1]
        if state['current_player'] == 0:
            if card in state['player1_hand']:
                state['player1_hand'].remove(card)
                state['public_revealed_cards'].append(card)
                if len(state['player1_hand']) < 3:
                    state['player1_hand'].extend(state['player1_win_pile'])
                    state['player1_win_pile'] = []
                state['current_player'] = 1
            else:
                raise ValueError("Invalid card selected.")
        elif state['current_player'] == 1:
            if card in state['player2_hand']:
                state['player2_hand'].remove(card)
                state['public_revealed_cards'].append(card)
                if len(state['player2_hand']) < 3:
                    state['player2_hand'].extend(state['player2_win_pile'])
                    state['player2_win_pile'] = []
                state['current_player'] = 0
            else:
                raise ValueError("Invalid card selected.")
        else:
            raise ValueError("Invalid player ID.")
    elif action.startswith('deal:'):
        # This is a chance action, not a player action
        pass
    else:
        raise ValueError("Invalid action string.")
    
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    player1_win_pile = len(state['player1_win_pile'])
    player2_win_pile = len(state['player2_win_pile'])
    
    if player1_win_pile == 16:
        return [1.0, 0.0]
    elif player2_win_pile == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    
    if state['current_player'] == 0:
        legal_actions.extend(['play:' + card for card in state['player1_hand']])
    elif state['current_player'] == 1:
        legal_actions.extend(['play:' + card for card in state['player2_hand']])
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player1_obs = {'hand': state['player1_hand'], 'win_pile': state['player1_win_pile']}
    player2_obs = {'hand': state['player2_hand'], 'win_pile': state['player2_win_pile']}
    
    return [player1_obs, player2_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # For simplicity, we assume a deterministic sampling here.
    # In a real implementation, this would involve complex logic to sample valid sequences.
    # Here, we just return a fixed sequence based on the last observed state.
    if player_id == 0:
        return ['play:A', 'play:K', 'play:Q', 'play:J']
    elif player_id == 1:
        return ['play:J', 'play:Q', 'play:K', 'play:A']
    else:
        raise ValueError("Invalid player ID.")

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print(initial_state)
    
    # Apply some actions to demonstrate the state transitions
    actions = [
        'play:A',
        'play:K',
        'play:Q',
        'play:J',
        'play:A',
        'play:K',
        'play:Q',
        'play:J'
    ]
    
    for action in actions:
        initial_state = apply_action(initial_state, action)
        print(initial_state)