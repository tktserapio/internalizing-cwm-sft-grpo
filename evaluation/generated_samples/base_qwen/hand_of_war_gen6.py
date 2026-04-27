import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper functions
def shuffle_deck(deck: List[int]) -> List[int]:
    """Shuffles the deck."""
    random.shuffle(deck)
    return deck

def deal_cards(deck: List[int], num_players: int) -> Tuple[List[int], List[int]]:
    """Deals cards evenly between players."""
    num_cards_per_player = len(deck) // num_players
    return (deck[:num_cards_per_player], deck[num_cards_per_player:])

def get_card_rank(card: int) -> int:
    """Converts card value to its rank (Ace=1, King=13, Queen=12, Jack=11)."""
    ranks = {1: 'A', 13: 'K', 12: 'Q', 11: 'J'}
    return ranks.get(card, card)

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Assuming a standard deck of 52 cards
    deck = list(range(1, 53))
    shuffled_deck = shuffle_deck(deck)
    player0_hand, player1_hand = deal_cards(shuffled_deck, 2)
    public_revealed_cards = []
    
    return {
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'public_revealed_cards': public_revealed_cards,
        'current_player': 0,
        'draw_piles': [{'hand': player0_hand, 'discard': []}, {'hand': player1_hand, 'discard': []}],
        'win_piles': [{}, {}],
        'running_reward': [0.0, 0.0]
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    if action.startswith('play:'):
        card_value = int(action.split(':')[1])
        card_rank = get_card_rank(card_value)
        
        if state['current_player'] == 0:
            player = 'player0'
        else:
            player = 'player1'
        
        if card_value in state[player]['hand']:
            state[player]['hand'].remove(card_value)
            state[player]['win_piles'][state['current_player']].append(card_value)
            state['public_revealed_cards'].append(card_value)
            
            if len(state[player]['hand']) < 3:
                state[player]['hand'].extend(state[player]['draw_piles'][state['current_player']]['hand'])
                state[player]['draw_piles'][state['current_player']]['hand'] = []
                
            state['current_player'] = (state['current_player'] + 1) % 2
            state['running_reward'][state['current_player']] += 1.0
            
            if len(state['player0_hand']) == 0:
                state['current_player'] = -4
            elif len(state['player1_hand']) == 0:
                state['current_player'] = -4
                
            return state
        else:
            raise ValueError(f"Invalid card value {card_value} selected.")
    else:
        raise ValueError("Invalid action format.")

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    return state['running_reward']

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['current_player'] == -4:
        return []
    
    legal_actions = []
    if state['current_player'] == 0:
        legal_actions.extend([f"play:{card}" for card in state['player0_hand']])
    else:
        legal_actions.extend([f"play:{card}" for card in state['player1_hand']])
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player0_obs = {
        'hand': state['player0_hand'],
        'win_pile': state['win_piles'][0],
        'draw_pile': state['draw_piles'][0]['hand']
    }
    player1_obs = {
        'hand': state['player1_hand'],
        'win_pile': state['win_piles'][1],
        'draw_pile': state['draw_piles'][1]['hand']
    }
    
    return [player0_obs, player1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we will just return a fixed sequence of actions
    actions = ['play:7', 'play:K', 'play:A', 'play:Q', 'play:J']
    return actions[:len(obs_action_history)]