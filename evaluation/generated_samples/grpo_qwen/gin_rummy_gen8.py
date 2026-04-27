import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to parse the game state
def parse_state(state_str: str) -> State:
    state_dict = eval(state_str)
    # Convert 'knock_card' to an integer for easier comparison
    state_dict['knock_card'] = int(state_dict['knock_card'])
    return state_dict

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial state with empty hands, no upcard, no discard, and no knock
    return {
        'upcard': None,
        'discard': None,
        'knock_card': 10,
        'players': [{'hand': [], 'deadwood': 0}, {'hand': [], 'deadwood': 0}],
        'phase': 'Draw',
        'wall': []
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player_id = 0 if new_state['current_player'] == '0' else 1
    player = new_state['players'][player_id]
    
    if action == 'Draw stock':
        new_state['wall'].append(new_state['stock'].pop())
        new_state['current_player'] = '0' if player_id == 1 else '1'
        return new_state
    
    if action == 'Draw upcard':
        new_state['upcard'] = new_state['stock'].pop()
        new_state['current_player'] = '0' if player_id == 1 else '1'
        return new_state
    
    if action.startswith('Action: '):
        card = action.split(':')[1]
        if card in player['hand']:
            player['hand'].remove(card)
            new_state['discard'] = card
            new_state['current_player'] = '0' if player_id == 1 else '1'
            return new_state
        else:
            return new_state
    
    if action == 'Knock':
        knock_card = new_state['knock_card']
        deadwood = sum([sum(1 for _ in group) * rank for rank, group in player['hand'].items()])
        if deadwood <= knock_card:
            new_state['knock'] = True
            new_state['knock_card'] = knock_card + 1
            new_state['current_player'] = '0' if player_id == 1 else '1'
            return new_state
        else:
            return new_state
    
    if action == 'Pass':
        new_state['current_player'] = '0' if player_id == 1 else '1'
        return new_state
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return int(state['current_player'])

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['knock']:
        return [state['knock_card'] - state['players'][int(state['current_player'])]['deadwood'], state['players'][int(not int(state['current_player']))]['deadwood']]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    player_id = 0 if state['current_player'] == '0' else 1
    player = state['players'][player_id]
    legal_actions = []
    
    if state['phase'] == 'Draw':
        legal_actions.append('Draw stock')
        legal_actions.append('Draw upcard')
    
    if state['phase'] == 'Knock':
        legal_actions.append('Knock')
        if state['knock']:
            legal_actions.append('Done')
    
    if state['knock']:
        legal_actions.append('Pass')
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        'upcard': state['upcard'],
        'discard': state['discard'],
        'knock_card': state['knock_card'],
        'wall': state['wall'],
        'phase': state['phase'],
        'deadwood': state['players'][0]['deadwood']
    }
    player_1_obs = {
        'upcard': state['upcard'],
        'discard': state['discard'],
        'knock_card': state['knock_card'],
        'wall': state['wall'],
        'phase': state['phase'],
        'deadwood': state['players'][1]['deadwood']
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    # For simplicity, we'll just return a random valid action
    actions = ['Draw stock', 'Draw upcard', 'Action: Ah', 'Knock', 'Pass']
    return [actions[int(player_id)]]