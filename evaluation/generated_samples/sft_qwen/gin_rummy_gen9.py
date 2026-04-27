import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = generate_deck()
    shuffled_deck = shuffle_deck(deck)
    player1_hand, player2_hand = deal_cards(shuffled_deck, 2)
    return {
        'player1_hand': player1_hand,
        'player2_hand': player2_hand,
        'upcard': None,
        'phase': 'Draw',
        'knock_card': 10,
        'dealer': 0,
        'round': 1,
        'history': [],
        'current_player': 0,
        'score': {'player1': 0, 'player2': 0},
        'deck': shuffled_deck,
        'wall': None
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    
    # Handle initial upcard decision
    if state['phase'] == 'Initial Upcard':
        if action == 'Draw upcard':
            new_state['upcard'] = new_state['deck'].pop(0)
            new_state['phase'] = 'Draw'
        elif action == 'Pass':
            new_state['phase'] = 'Draw'
        else:
            raise ValueError(f"Invalid action {action} for Initial Upcard phase.")
    
    # Handle draw phase
    elif state['phase'] == 'Draw':
        if action == 'Draw stock':
            new_state['upcard'] = new_state['deck'].pop(0)
            new_state['phase'] = 'Discard'
        elif action == 'Draw upcard':
            new_state['upcard'] = new_state['deck'].pop(0)
            new_state['phase'] = 'Discard'
        elif action.startswith('Action: '):
            new_state['upcard'] = None
            new_state['phase'] = 'Discard'
            new_state['current_player'] = 1 - state['current_player']
            new_state['player1_hand'], new_state['player2_hand'] = deal_cards(new_state['deck'], 2)
        else:
            raise ValueError(f"Invalid action {action} in Draw phase.")
    
    # Handle discard phase
    elif state['phase'] == 'Discard':
        if action == 'Action: Knock':
            new_state['phase'] = 'Knock'
            new_state['knock_card'] = 10
            new_state['knock_phase'] = 1
            new_state['knock_player'] = state['current_player']
            new_state['knock_melds'] = []
            new_state['knock_deadwood'] = 0
            new_state['knock_opponent_melds'] = []
            new_state['knock_opponent_deadwood'] = 0
        elif action == 'Action: Done':
            new_state['phase'] = 'Layoff'
            new_state['knock_phase'] = 2
        elif action.startswith('Action: '):
            card_to_discard = action.split(':')[1]
            if card_to_discard in new_state['player1_hand']:
                new_state['player1_hand'].remove(card_to_discard)
            elif card_to_discard in new_state['player2_hand']:
                new_state['player2_hand'].remove(card_to_discard)
            else:
                raise ValueError(f"Invalid card {card_to_discard} in discard phase.")
            new_state['phase'] = 'Knock'
            new_state['knock_phase'] = 1
            new_state['knock_player'] = state['current_player']
            new_state['knock_melds'] = []
            new_state['knock_deadwood'] = 0
            new_state['knock_opponent_melds'] = []
            new_state['knock_opponent_deadwood'] = 0
        else:
            raise ValueError(f"Invalid action {action} in Discard phase.")
    
    # Handle knock phase
    elif state['phase'] == 'Knock':
        if action == 'Action: Knock':
            new_state['phase'] = 'Layoff'
            new_state['knock_phase'] = 2
        elif action.startswith('Action: '):
            card_to_discard = action.split(':')[1]
            if card_to_discard in new_state['player1_hand']:
                new_state['player1_hand'].remove(card_to_discard)
            elif card_to_discard in new_state['player2_hand']:
                new_state['player2_hand'].remove(card_to_discard)
            else:
                raise ValueError(f"Invalid card {card_to_discard} in knock phase.")
            new_state['knock_phase'] = 1
            new_state['knock_player'] = state['current_player']
            new_state['knock_melds'] = []
            new_state['knock_deadwood'] = 0
            new_state['knock_opponent_melds'] = []
            new_state['knock_opponent_deadwood'] = 0
        else:
            raise ValueError(f"Invalid action {action} in Knock phase.")
    
    # Handle layoff phase
    elif state['phase'] == 'Layoff':
        if action.startswith('Action: '):
            card_to_layoff = action.split(':')[1]
            if card_to_layoff in new_state['player1_hand']:
                new_state['player1_hand'].remove(card_to_layoff)
            elif card_to_layoff in new_state['player2_hand']:
                new_state['player2_hand'].remove(card_to_layoff)
            else:
                raise ValueError(f"Invalid card {card_to_layoff} in layoff phase.")
            new_state['knock_phase'] = 3
        else:
            raise ValueError(f"Invalid action {action} in Layoff phase.")
    
    # Handle wall phase
    elif state['phase'] == 'Wall':
        if action == 'Action: Draw stock':
            new_state['upcard'] = new_state['deck'].pop(0)
            new_state['phase'] = 'Draw'
        elif action == 'Action: Draw upcard':
            new_state['upcard'] = new_state['deck'].pop(0)
            new_state['phase'] = 'Discard'
        elif action.startswith('Action: '):
            card_to_discard = action.split(':')[1]
            if card_to_discard in new_state['player1_hand']:
                new_state['player1_hand'].remove(card_to_discard)
            elif card_to_discard in new_state['player2_hand']:
                new_state['player2_hand'].remove(card_to_discard)
            else:
                raise ValueError(f"Invalid card {card_to_discard} in wall phase.")
            new_state['phase'] = 'Knock'
            new_state['knock_phase'] = 1
            new_state['knock_player'] = state['current_player']
            new_state['knock_melds'] = []
            new_state['knock_deadwood'] = 0
            new_state['knock_opponent_melds'] = []
            new_state['knock_opponent_deadwood'] = 0
        else:
            raise ValueError(f"Invalid action {action} in Wall phase.")
    
    # Handle terminal state
    elif state['phase'] == 'Terminal':
        if action == 'Pass':
            new_state['phase'] = 'Terminal'
        else:
            raise ValueError(f"Invalid action {action} in Terminal state.")
    
    # Update history
    new_state['history'].append((state['current_player'], action))
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['phase'] == 'Terminal':
        return [state['score']['player1'], state['score']['player2']]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['phase'] == 'Initial Upcard':
        return ['Draw upcard', 'Pass']
    elif state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    elif state['phase'] == 'Discard':
        if state['current_player'] == 0:
            return ['Action: ' + card for card in state['player1_hand']] + ['Action: Knock']
        else:
            return ['Action: ' + card for card in state['player2_hand']] + ['Action: Knock']
    elif state['phase'] == 'Knock':
        if state['current_player'] == 0:
            return ['Action: Knock', 'Action: Done']
        else:
            return ['Action: Knock']
    elif state['phase'] == 'Layoff':
        if state['current_player'] == 0:
            return ['Action: ' + card for card in state['player1_hand']] + ['Action: Done']
        else:
            return ['Action: ' + card for card in state['player2_hand']] + ['Action: Done']
    elif state['phase'] == 'Wall':
        if state['current_player'] == 0:
            return ['Action: Draw stock', 'Action: Draw upcard']
        else:
            return ['Action: Draw stock', 'Action: Draw upcard']
    elif state['phase'] == 'Terminal':
        return []

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player1_obs = {
        'upcard': state['upcard'],
        'player1_hand': state['player1_hand'],
        'player2_hand': state['player2_hand'],
        'knock_card': state['knock_card'],
        'knock_phase': state['knock_phase'],
        'knock_player': state['knock_player'],
        'knock_melds': state['knock_melds'],
        'knock_deadwood': state['knock_deadwood'],
        'knock_opponent_melds': state['knock_opponent_melds'],
        'knock_opponent_deadwood': state['knock_opponent_deadwood'],
        'wall': state['wall']
    }
    player2_obs = {
        'upcard': state['upcard'],
        'player1_hand': state['player2_hand'],
        'player2_hand': state['player1_hand'],
        'knock_card': state['knock_card'],
        'knock_phase': state['knock_phase'],
        'knock_player': state['knock_player'],
        'knock_melds': state['knock_melds'],
        'knock_deadwood': state['knock_deadwood'],
        'knock_opponent_melds': state['knock_opponent_melds'],
        'knock_opponent_deadwood': state['knock_opponent_deadwood'],
        'wall': state['wall']
    }
    return [player1_obs, player2_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ['Action: 2c', 'Action: 3c', 'Action: 4c', 'Action: Knock']
    else:
        return ['Action: 2c', 'Action: 3c', 'Action: 4c', 'Action: Knock']