import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

def initialize_deck() -> List[int]:
    """Initialize a shuffled deck of 52 cards."""
    suits = ['S', 'C', 'D', 'H']
    ranks = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A']
    deck = [(rank, suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def create_initial_state(deck: List[int]) -> State:
    """Create the initial state of the game."""
    # Initialize the state with the deck, player hands, discard pile, and stock pile
    state = {
        'deck': deck,
        'discard_pile': [],
        'stock_pile': deck,
        'players': [{'hand': [], 'score': 0}, {'hand': [], 'score': 0}],
        'current_player': 0,
        'phase': 'Draw',
        'knock_card': 10,
        'knocked': False,
        'upcard': None,
        'wall': False
    }
    return state

def draw_card(state: State, player_id: int) -> State:
    """Draw a card from the stock pile."""
    if len(state['stock_pile']) == 0:
        state['wall'] = True
        return state
    card = state['stock_pile'].pop()
    state['players'][player_id]['hand'].append(card)
    return state

def discard_card(state: State, player_id: int, card: int) -> State:
    """Discard a card from the player's hand."""
    if len(state['players'][player_id]['hand']) == 0:
        return state
    state['players'][player_id]['hand'].remove(card)
    state['discard_pile'].append(card)
    return state

def get_deadwood_value(hand: List[int], knock_card: int) -> int:
    """Calculate the deadwood value of the given hand."""
    deadwood_value = 0
    for card in hand:
        if card > 10:
            deadwood_value += 10
        elif card == 1:
            deadwood_value += 1
        else:
            deadwood_value += card
    return deadwood_value

def get_knockable_state(state: State, player_id: int, knock_card: int) -> bool:
    """Check if the current player can knock based on the knock card value."""
    deadwood_value = get_deadwood_value(state['players'][player_id]['hand'], knock_card)
    return deadwood_value <= knock_card

def get_melds(hand: List[int]) -> List[List[int]]:
    """Generate all possible melds from the given hand."""
    melds = []
    for i in range(len(hand)):
        for j in range(i+1, len(hand)):
            for k in range(j+1, len(hand)):
                if hand[i][0] == hand[j][0] == hand[k][0]:  # Set
                    melds.append([hand[i], hand[j], hand[k]])
                elif hand[i][1] == hand[j][1] == hand[k][1] and abs(hand[i][0] - hand[j][0]) == 1 and abs(hand[j][0] - hand[k][0]) == 1:  # Run
                    melds.append([hand[i], hand[j], hand[k]])
    return melds

def get_legal_actions(state: State, player_id: int) -> List[Action]:
    """Return the legal actions for the current player."""
    legal_actions = []
    if state['phase'] == 'Draw':
        if player_id == state['current_player']:
            if len(state['stock_pile']) > 0:
                legal_actions.append('Draw stock')
            if len(state['discard_pile']) > 0:
                legal_actions.append('Draw upcard')
        else:
            legal_actions.append('Pass')
    elif state['phase'] == 'Knock':
        if player_id == state['current_player']:
            if not state['knocked']:
                legal_actions.append('Action: Knock')
            else:
                legal_actions.append('Action: Done')
        else:
            legal_actions.append('Pass')
    return legal_actions

def apply_action(state: State, action: Action, player_id: int) -> State:
    """Apply the given action to the state."""
    new_state = state.copy()
    if action == 'Draw stock':
        new_state = draw_card(new_state, player_id)
    elif action == 'Draw upcard':
        new_state = draw_card(new_state, player_id)
    elif action.startswith('Action: '):
        card = int(action.split(': ')[1])
        new_state = discard_card(new_state, player_id, card)
    elif action == 'Action: Knock':
        new_state = knock_round(new_state, player_id)
    elif action == 'Action: Done':
        new_state['knocked'] = True
    elif action == 'Pass':
        new_state['current_player'] = (player_id + 1) % 2
    return new_state

def knock_round(state: State, player_id: int) -> State:
    """Handle the knock round logic."""
    if not get_knockable_state(state, player_id, state['knock_card']):
        raise ValueError("Cannot knock with invalid deadwood value.")
    
    state['knocked'] = True
    state['knock_card'] = 10  # Reset knock card for next round
    
    # Lay down the hand
    melds = get_melds(state['players'][player_id]['hand'])
    deadwood = [card for card in state['players'][player_id]['hand'] if card not in melds]
    
    # Declare melds
    for meld in melds:
        state['players'][player_id]['hand'].remove(meld)
        state['players'][player_id]['hand'].extend(meld)
    
    # Declare deadwood
    state['players'][player_id]['hand'].extend(deadwood)
    
    # Determine the opponent's hand
    opponent_hand = state['players'][1 - player_id]['hand']
    
    # Lay off
    for card in deadwood:
        if card in opponent_hand:
            opponent_hand.remove(card)
            state['players'][player_id]['hand'].append(card)
    
    # Calculate scores
    knocker_score = get_deadwood_value(state['players'][player_id]['hand'], state['knock_card'])
    opponent_score = get_deadwood_value(opponent_hand, state['knock_card'])
    
    if knocker_score < opponent_score:
        return state
    elif knocker_score == opponent_score:
        return state
    else:
        return state

def get_current_player(state: State) -> int:
    """Get the current player ID."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Get the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Get the rewards for each player."""
    knocker_score = get_deadwood_value(state['players'][state['current_player']]['hand'], state['knock_card'])
    opponent_score = get_deadwood_value(state['players'][1 - state['current_player']]['hand'], state['knock_card'])
    if state['knocked']:
        if knocker_score < opponent_score:
            return [knocker_score, opponent_score]
        elif knocker_score == opponent_score:
            return [0.0, 0.0]
        else:
            return [0.0, 0.0]
    else:
        return [0.0, 0.0]

def get_observations(state: State) -> List[PlayerObservation]:
    """Get the observations for each player."""
    knocker_obs = {
        'deadwood': get_deadwood_value(state['players'][state['current_player']]['hand'], state['knock_card']),
        'melds': state['players'][state['current_player']]['hand'],
        'phase': state['phase'],
        'upcard': state['upcard'],
        'knock_card': state['knock_card'],
        'wall': state['wall']
    }
    opponent_obs = {
        'deadwood': get_deadwood_value(state['players'][1 - state['current_player']]['hand'], state['knock_card']),
        'melds': state['players'][1 - state['current_player']]['hand'],
        'phase': state['phase'],
        'upcard': state['upcard'],
        'knock_card': state['knock_card'],
        'wall': state['wall']
    }
    return [knocker_obs, opponent_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Resample a valid sequence of actions."""
    # Placeholder for resampling logic
    return obs_action_history[-1][1]