import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

def initialize_deck() -> List[int]:
    """Initializes a shuffled deck of cards."""
    suits = ['Spades', 'Clubs', 'Diamonds', 'Hearts']
    ranks = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
    deck = [(suit, rank) for suit in suits for rank in ranks]
    shuffle(deck)
    return deck

def convert_card(card: Tuple[str, str]) -> int:
    """Converts a card tuple to a numeric value."""
    return 1 + ranks.index(card[1]) * 13 + suits.index(card[0])

def convert_numeric(card: int) -> Tuple[str, str]:
    """Converts a numeric value back to a card tuple."""
    rank_index = card % 13
    suit_index = (card // 13) % 4
    rank = ranks[rank_index]
    suit = suits[suit_index]
    return (suit, rank)

def split_hand(hand: List[int], num_players: int) -> List[List[int]]:
    """Splits the hand into two hands for two players."""
    return [hand[i::num_players] for i in range(num_players)]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = initialize_deck()
    hand0, hand1 = split_hand(deck, 2)
    state = {
        'deck': deck,
        'hand0': hand0,
        'hand1': hand1,
        'upcard': None,
        'phase': 'Draw',
        'knock_card': 10,
        'knocked': False,
        'deadwood0': 0,
        'deadwood1': 0,
        'meld0': [],
        'meld1': [],
        'meld0_made': False,
        'meld1_made': False,
        'player0_turn': True,
        'player1_turn': False,
        'player0_score': 0,
        'player1_score': 0,
        'player0_melds': [],
        'player1_melds': [],
        'player0_deadwood': [],
        'player1_deadwood': [],
        'player0_melds_made': False,
        'player1_melds_made': False,
        'player0_layoffs': [],
        'player1_layoffs': []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['deck'].append(new_state['hand0'].pop(0))
        new_state['upcard'] = new_state['hand0'][0]
        new_state['phase'] = 'Discard'
        new_state['player0_turn'] = not new_state['player0_turn']
    elif action == 'Draw upcard':
        new_state['deck'].append(new_state['hand0'].pop(0))
        new_state['upcard'] = new_state['hand0'][0]
        new_state['phase'] = 'Discard'
        new_state['player0_turn'] = not new_state['player0_turn']
    elif action.startswith('Action: '):
        card_to_discard = int(action[7:])
        new_state['hand0'].remove(card_to_discard)
        new_state['deadwood0'] += convert_card(card_to_discard)
        new_state['meld0'].append(card_to_discard)
        new_state['meld0_made'] = True
        new_state['player0_turn'] = not new_state['player0_turn']
    elif action == 'Action: Knock':
        new_state['knocked'] = True
        new_state['player0_turn'] = not new_state['player0_turn']
        new_state['phase'] = 'Knock'
        new_state['deadwood0'] = sum(convert_card(card) for card in new_state['hand0'] if card not in new_state['meld0'])
        new_state['deadwood1'] = sum(convert_card(card) for card in new_state['hand1'] if card not in new_state['meld1'])
        new_state['meld0_made'] = True
        new_state['meld1_made'] = True
    elif action == 'Action: Done':
        new_state['knocked'] = True
        new_state['player0_turn'] = not new_state['player0_turn']
        new_state['phase'] = 'Layoff'
    elif action == 'Pass':
        new_state['player0_turn'] = not new_state['player0_turn']
        new_state['phase'] = 'Draw'
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state