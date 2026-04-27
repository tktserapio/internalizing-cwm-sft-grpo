import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initialize the deck
    deck = initialize_deck()
    # Shuffle the deck
    deck = shuffle_deck(deck)
    # Split the deck into two hands
    player1_hand, player2_hand = split_deck(deck, 2)
    # Create the initial state
    state = {
        'deck': deck,
        'player1_hand': player1_hand,
        'player2_hand': player2_hand,
        'upcard': None,
        'phase': 'Draw',
        'knock_card': None,
        'player1_melds': [],
        'player2_melds': [],
        'player1_deadwood': 0,
        'player2_deadwood': 0,
        'player1_knocked': False,
        'player2_knocked': False,
        'player1_layoff_cards': [],
        'player2_layoff_cards': [],
        'player1_score': 0,
        'player2_score': 0,
        'current_player': 0,
        'observation_window': []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    
    if action == 'Draw stock':
        if state['knock_card'] is None:
            new_state['upcard'] = state['deck'].pop(0)
            new_state['phase'] = 'Discard'
        else:
            new_state['knock_card'] = None
            new_state['upcard'] = state['deck'].pop(0)
            new_state['phase'] = 'Knock'
    
    elif action == 'Draw upcard':
        if state['knock_card'] is None:
            new_state['upcard'] = state['deck'].pop(0)
            new_state['phase'] = 'Discard'
        else:
            new_state['knock_card'] = None
            new_state['upcard'] = state['deck'].pop(0)
            new_state['phase'] = 'Knock'
    
    elif action.startswith('Action: '):
        card_to_discard = action.split(':')[1]
        if card_to_discard in state['player1_hand']:
            new_state['player1_hand'].remove(card_to_discard)
            new_state['player1_deadwood'] += 1
            if state['knock_card'] is None:
                new_state['phase'] = 'Discard'
            else:
                new_state['knock_card'] = None
                new_state['phase'] = 'Knock'
        else:
            raise ValueError(f"Card {card_to_discard} not found in player1_hand")
    
    elif action == 'Action: Knock':
        if state['knock_card'] is None:
            new_state['knock_card'] = 10
            new_state['phase'] = 'Knock'
        else:
            new_state['knock_card'] = None
            new_state['phase'] = 'Layoff'
    
    elif action == 'Action: Done':
        if state['knock_card'] is None:
            new_state['knock_card'] = 10
            new_state['phase'] = 'Knock'
        else:
            new_state['knock_card'] = None
            new_state['phase'] = 'Layoff'
    
    elif action == 'Pass':
        if state['knock_card'] is None:
            new_state['knock_card'] = 10
            new_state['phase'] = 'Knock'
        else:
            new_state['knock_card'] = None
            new_state['phase'] = 'Layoff'
    
    elif action == 'deal:':
        # Handle the case where the stock pile is exhausted
        new_state['phase'] = 'Wall'
    
    else:
        raise ValueError(f"Invalid action: {action}")
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['knock_card'] is None:
        return state['current_player']
    else:
        return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['phase'] == 'Wall':
        return [0.0, 0.0]
    else:
        return [state['player1_score'], state['player2_score']]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['phase'] == 'Wall':
        return []
    elif state['knock_card'] is None:
        if state['phase'] == 'Draw':
            return ['Draw stock', 'Draw upcard']
        else:
            return ['Action: 2c', 'Action: 3d', 'Action: 4s', 'Action: 5h', 'Action: 6s', 'Action: 7c', 'Action: 8d', 'Action: 9t', 'Action: 10h', 'Action: Ac', 'Action: 2d', 'Action: 3s', 'Action: 4h', 'Action: 5s', 'Action: 6c', 'Action: 7d', 'Action: 8s', 'Action: 9c', 'Action: 10s', 'Action: As', 'Action: Jc', 'Action: Jd', 'Action: Jh', 'Action: Js', 'Action: Qc', 'Action: Qd', 'Action: Qh', 'Action: Qs', 'Action: Kc', 'Action: Kd', 'Action: Kh', 'Action: Ks', 'Action: Done', 'Pass']
    else:
        return ['Action: Done']

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player1_obs = {
        'upcard': state['upcard'],
        'player1_hand': state['player1_hand'],
        'player1_melds': state['player1_melds'],
        'player1_deadwood': state['player1_deadwood'],
        'knock_card': state['knock_card'],
        'phase': state['phase'],
        'player1_score': state['player1_score'],
        'player2_score': state['player2_score'],
        'player1_melds': state['player1_melds'],
        'player2_melds': state['player2_melds'],
        'player1_layoff_cards': state['player1_layoff_cards'],
        'player2_layoff_cards': state['player2_layoff_cards'],
        'observation_window': state['observation_window']
    }
    player2_obs = {
        'upcard': state['upcard'],
        'player2_hand': state['player2_hand'],
        'player2_melds': state['player2_melds'],
        'player2_deadwood': state['player2_deadwood'],
        'knock_card': state['knock_card'],
        'phase': state['phase'],
        'player1_score': state['player1_score'],
        'player2_score': state['player2_score'],
        'player1_melds': state['player1_melds'],
        'player2_melds': state['player2_melds'],
        'player1_layoff_cards': state['player1_layoff_cards'],
        'player2_layoff_cards': state['player2_layoff_cards'],
        'observation_window': state['observation_window']
    }
    return [player1_obs, player2_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ['Draw stock', 'Action: 2c', 'Action: 3d', 'Action: 4s', 'Action: 5h', 'Action: 6s', 'Action: 7c', 'Action: 8d', 'Action: 9t', 'Action: 10h', 'Action: Ac', 'Action: 2d', 'Action: 3s', 'Action: 4h', 'Action: 5s', 'Action: 6c', 'Action: 7d', 'Action: 8s', 'Action: 9c', 'Action: 10s', 'Action: As', 'Action: Jc', 'Action: Jd', 'Action: Jh', 'Action: Js', 'Action: Qc', 'Action: Qd', 'Action: Qh', 'Action: Qs', 'Action: Kc', 'Action: Kd', 'Action: Kh', 'Action: Ks', 'Action: Done', 'Pass']
    else:
        return ['Draw stock', 'Action: 2c', 'Action: 3d', 'Action: 4s', 'Action: 5h', 'Action: 6s', 'Action: 7c', 'Action: 8d', 'Action: 9t', 'Action: 10h', 'Action: Ac', 'Action: 2d', 'Action: 3s', 'Action: 4h', 'Action: 5s', 'Action: 6c', 'Action: 7d', 'Action: 8s', 'Action: 9c', 'Action: 10s', 'Action: As', 'Action: Jc', 'Action: Jd', 'Action: Jh', 'Action: Js', 'Action: Qc', 'Action: Qd', 'Action: Qh', 'Action: Qs', 'Action: Kc', 'Action: Kd', 'Action: Kh', 'Action: Ks', 'Action: Done', 'Pass']