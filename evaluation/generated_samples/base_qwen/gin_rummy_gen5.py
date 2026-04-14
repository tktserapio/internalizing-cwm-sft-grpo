import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Dict, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def shuffle_deck() -> List[int]:
    """Shuffles a standard 52-card deck and returns the shuffled list."""
    suits = ['Spades', 'Clubs', 'Diamonds', 'Hearts']
    ranks = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
    deck = [(suit, rank) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def create_initial_state(deck: List[int]) -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial state includes the deck, the player hands, and the discard pile
    return {
        'deck': deck,
        'player_hands': [{'cards': [], 'deadwood': 0}, {'cards': [], 'deadwood': 0}],
        'discard_pile': [],
        'current_player': 0,
        'knock_card': 10,
        'phase': 'Draw',
        'wall': False
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['deck'] = new_state['deck'][1:] + new_state['discard_pile']
        new_state['discard_pile'].pop()
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        new_state['phase'] = 'Draw'
    elif action == 'Draw upcard':
        new_state['deck'] = new_state['deck'][1:] + new_state['discard_pile']
        new_state['discard_pile'].pop()
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        new_state['phase'] = 'Draw'
    elif action.startswith('Action: '):
        card_to_discard = action.split(':')[1]
        new_state['player_hands'][new_state['current_player']]['cards'].remove(card_to_discard)
        new_state['discard_pile'].append(card_to_discard)
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        new_state['phase'] = 'Discard'
    elif action == 'Knock':
        new_state['knock_card'] = 10
        new_state['phase'] = 'Knock'
    elif action == 'Done':
        new_state['phase'] = 'Knock'
    elif action == 'Pass':
        new_state['phase'] = 'Knock'
    else:
        raise ValueError(f"Invalid action: {action}")
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['phase'] == 'Knock':
        return [0.0, 0.0]
    elif state['phase'] == 'Wall':
        return [-1.0, -1.0]  # Both players lose
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['phase'] == 'Wall':
        return []
    elif state['phase'] == 'Knock':
        return ['Knock', 'Done', 'Pass']
    elif state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    else:
        return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_cards = state['player_hands'][0]['cards']
    player_1_cards = state['player_hands'][1]['cards']
    player_0_deadwood = sum([1 if card in player_0_cards else 0 for card in player_0_cards])
    player_1_deadwood = sum([1 if card in player_1_cards else 0 for card in player_1_cards])
    
    player_0_obs = {
        'deck': state['deck'],
        'player_hands': [{'cards': player_0_cards, 'deadwood': player_0_deadwood}],
        'discard_pile': state['discard_pile'],
        'current_player': state['current_player'],
        'knock_card': state['knock_card'],
        'phase': state['phase'],
        'wall': state['wall']
    }
    
    player_1_obs = {
        'deck': state['deck'],
        'player_hands': [{'cards': player_1_cards, 'deadwood': player_1_deadwood}],
        'discard_pile': state['discard_pile'],
        'current_player': state['current_player'],
        'knock_card': state['knock_card'],
        'phase': state['phase'],
        'wall': state['wall']
    }
    
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # For simplicity, we'll just randomly select actions from the possible ones
    possible_actions = get_legal_actions(obs_action_history[-1][0])
    sampled_actions = [random.choice(possible_actions) for _ in range(len(obs_action_history))]
    
    # Ensure the sampled actions match the observed history
    for i, (obs, _) in enumerate(obs_action_history):
        if obs['current_player'] != player_id:
            continue
        if sampled_actions[i] not in possible_actions:
            raise ValueError(f"Incorrect action sampled: {sampled_actions[i]}")
    
    return sampled_actions