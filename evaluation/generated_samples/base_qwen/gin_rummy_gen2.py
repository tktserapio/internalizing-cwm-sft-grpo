import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Dict, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def shuffle_deck() -> List[int]:
    """Shuffles the deck and returns the order of cards."""
    deck = list(range(1, 53))
    random.shuffle(deck)
    return deck

def create_initial_state(deck: List[int]) -> State:
    """Creates the initial game state."""
    # Initial state setup
    state = {
        'deck': deck,
        'upcard': deck.pop(0),
        'dealer': 0,  # Assume player 0 is the dealer
        'phase': 'Draw',
        'knock_card': 10,  # Default knock card value
        'player_0_melds': [],
        'player_1_melds': [],
        'player_0_deadwood': 0,
        'player_1_deadwood': 0,
        'player_0_hand': deck[:13],
        'player_1_hand': deck[13:26],
        'player_0_turn': True,
        'player_1_turn': False,
        'knocked': False,
        'player_0_melds_count': 0,
        'player_1_melds_count': 0,
        'player_0_melds_value': 0,
        'player_1_melds_value': 0,
        'player_0_deadwood_value': 0,
        'player_1_deadwood_value': 0,
        'player_0_melds_list': [],
        'player_1_melds_list': [],
        'player_0_melds_count_list': [],
        'player_1_melds_count_list': [],
        'player_0_melds_value_list': [],
        'player_1_melds_value_list': [],
        'player_0_deadwood_value_list': [],
        'player_1_deadwood_value_list': []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Applies an action to the current state and returns the new state."""
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['upcard'] = state['deck'].pop(0)
    elif action.startswith('Action: '):
        card_to_discard = action[8:]
        if card_to_discard in new_state['player_0_hand']:
            new_state['player_0_hand'].remove(card_to_discard)
            new_state['player_0_deadwood'] += new_state['player_0_hand'].count(int(card_to_discard)) * new_state['player_0_hand'][int(card_to_discard) - 1]
            new_state['player_0_deadwood_value'] += new_state['player_0_hand'].count(int(card_to_discard)) * new_state['player_0_hand'][int(card_to_discard) - 1]
            new_state['player_0_melds_value'] -= new_state['player_0_hand'].count(int(card_to_discard)) * new_state['player_0_hand'][int(card_to_discard) - 1]
            new_state['player_0_melds_count'] -= new_state['player_0_hand'].count(int(card_to_discard))
            new_state['player_0_melds_value_list'].append(new_state['player_0_melds_value'])
            new_state['player_0_melds_count_list'].append(new_state['player_0_melds_count'])
            new_state['player_0_melds_list'].append(new_state['player_0_melds'])
            new_state['player_0_deadwood_value_list'].append(new_state['player_0_deadwood_value'])
            new_state['player_0_deadwood_count'] -= new_state['player_0_hand'].count(int(card_to_discard))
            new_state['player_0_deadwood_value'] -= new_state['player_0_hand'].count(int(card_to_discard)) * new_state['player_0_hand'][int(card_to_discard) - 1]
            new_state['player_0_hand'].append(card_to_discard)
            new_state['player_0_deadwood'] += new_state['player_0_hand'].count(int(card_to_discard)) * new_state['player_0_hand'][int(card_to_discard) - 1]
            new_state['player_0_deadwood_value'] += new_state['player_0_hand'].count(int(card_to_discard)) * new_state['player_0_hand'][int(card_to_discard) - 1]
            new_state['player_0_melds_value'] += new_state['player_0_hand'].count(int(card_to_discard)) * new_state['player_0_hand'][int(card_to_discard) - 1]
            new_state['player_0_melds_count'] += new_state['player_0_hand'].count(int(card_to_discard))
            new_state['player_0_melds_value_list'].append(new_state['player_0_melds_value'])
            new_state['player_0_melds_count_list'].append(new_state['player_0_melds_count'])
            new_state['player_0_melds_list'].append(new_state['player_0_melds'])
            new_state['player_0_deadwood_value_list'].append(new_state['player_0_deadwood_value'])
        else:
            print(f"Invalid card to discard: {card_to_discard}")
    elif action == 'Action: Knock':
        new_state['knocked'] = True
        new_state['phase'] = 'Knock'
        new_state['knock_card'] = 10
        new_state['player_0_melds_value'] = sum([sum(meld) for meld in new_state['player_0_melds']])
        new_state['player_1_melds_value'] = sum([sum(meld) for meld in new_state['player_1_melds']])
        new_state['player_0_deadwood_value'] = sum(new_state['player_0_deadwood_value_list'])
        new_state['player_1_deadwood_value'] = sum(new_state['player_1_deadwood_value_list'])
        new_state['player_0_melds_count'] = sum(new_state['player_0_melds_count_list'])
        new_state['player_1_melds_count'] = sum(new_state['player_1_melds_count_list'])
        new_state['player_0_melds_value_list'] = new_state['player_0_melds_value_list']
        new_state['player_0_melds_count_list'] = new_state['player_0_melds_count_list']
        new_state['player_0_melds_list'] = new_state['player_0_melds_list']
        new_state['player_0_deadwood_value_list'] = new_state['player_0_deadwood_value_list']
        new_state['player_1_melds_value_list'] = new_state['player_1_melds_value_list']
        new_state['player_1_melds_count_list'] = new_state['player_1_melds_count_list']
        new_state['player_1_melds_list'] = new_state['player_1_melds_list']
        new_state['player_1_deadwood_value_list'] = new_state['player_1_deadwood_value_list']
    elif action == 'Action: Done':
        new_state['phase'] = 'Layoff'
        new_state['player_0_melds_value'] = sum([sum(meld) for meld in new_state['player_0_melds']])
        new_state['player_1_melds_value'] = sum([sum(meld) for meld in new_state['player_1_melds']])
        new_state['player_0_deadwood_value'] = sum(new_state['player_0_deadwood_value_list'])
        new_state['player_1_deadwood_value'] = sum(new_state['player_1_deadwood_value_list'])
        new_state['player_0_melds_count'] = sum(new_state['player_0_melds_count_list'])
        new_state['player_1_melds_count'] = sum(new_state['player_1_melds_count_list'])
        new_state['player_0_melds_value_list'] = new_state['player_0_melds_value_list']
        new_state['player_0_melds_count_list'] = new_state['player_0_melds_count_list']
        new_state['player_0_melds_list'] = new_state['player_0_melds_list']
        new_state['player_0_deadwood_value_list'] = new_state['player_0_deadwood_value_list']
        new_state['player_1_melds_value_list'] = new_state['player_1_melds_value_list']
        new_state['player_1_melds_count_list'] = new_state['player_1_melds_count_list']
        new_state['player_1_melds_list'] = new_state['player_1_melds_list']
        new_state['player_1_deadwood_value_list'] = new_state['player_1_deadwood_value_list']
    elif action == 'Pass':
        new_state['phase'] = 'Wall'
        new_state['knocked'] = False
    else:
        print(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    """Returns the current player based on the state."""
    return state['player_0_turn']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player based on the state."""
    if state['knocked']:
        if state['player_0_deadwood_value'] <= state['knock_card']:
            return [state['player_0_deadwood_value'], state['player_1_deadwood_value']]
        elif state['player_1_deadwood_value'] <= state['knock_card']:
            return [state['player_1_deadwood_value'], state['player_0_deadwood_value']]
        else:
            return [state['player_0_deadwood_value'] + 25, state['player_1_deadwood_value'] + 25]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns the legal actions for the current state."""
    player_id = get_current_player(state)
    if state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    elif state['phase'] == 'Knock':
        return ['Action: Knock', 'Action: Done']
    elif state['phase'] == 'Layoff':
        return ['Action: Done']
    elif state['phase'] == 'Wall':
        return ['Pass']
    else:
        return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns the observations for each player based on the state."""
    player_0_obs = {
        'upcard': state['upcard'],
        'player_0_hand': state['player_0_hand'],
        'player_0_deadwood': state['player_0_deadwood'],
        'player_0_melds': state['player_0_melds'],
        'player_0_melds_value': state['player_0_melds_value'],
        'player_0_melds_count': state['player_0_melds_count'],
        'player_0_melds_list': state['player_0_melds_list'],
        'player_0_melds_value_list': state['player_0_melds_value_list'],
        'player_0_melds_count_list': state['player_0_melds_count_list'],
        'player_0_deadwood_value_list': state['player_0_deadwood_value_list']
    }
    player_1_obs = {
        'upcard': state['upcard'],
        'player_1_hand': state['player_1_hand'],
        'player_1_deadwood': state['player_1_deadwood'],
        'player_1_melds': state['player_1_melds'],
        'player_1_melds_value': state['player_1_melds_value'],
        'player_1_melds_count': state['player_1_melds_count'],
        'player_1_melds_list': state['player_1_melds_list'],
        'player_1_melds_value_list': state['player_1_melds_value_list'],
        'player_1_melds_count_list': state['player_1_melds_count_list'],
        'player_1_deadwood_value_list': state['player_1_deadwood_value_list']
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically samples a valid sequence of actions that explains the current observations."""
    # Implementing this function would require a more complex algorithm to handle the stochastic nature of the game.
    # For simplicity, we'll just return a fixed sequence of actions.
    # This is a placeholder function and should be replaced with a proper implementation.
    if player_id == 0:
        return ['Draw stock', 'Action: 3d', 'Action: Knock']
    else:
        return ['Draw stock', 'Action: 3d', 'Action: Knock']

# Example usage
initial_deck = shuffle_deck()
initial_state = create_initial_state(initial_deck)
print("Initial State:", initial_state)

# Apply actions
new_state = apply_action(initial_state, 'Draw stock')
print("After Draw stock:", new_state)

new_state = apply_action(new_state, 'Action: 3d')
print("After Action: 3d:", new_state)

new_state = apply_action(new_state, 'Action: Knock')
print("After Action: Knock:", new_state)

# Get legal actions
legal_actions = get_legal_actions(new_state)
print("Legal Actions:", legal_actions)

# Get observations
observations = get_observations(new_state)
print("Observations:", observations)

# Resample history
resampled_actions = resample_history([(obs, None) for obs in observations], 0)
print("Resampled Actions:", resampled_actions)