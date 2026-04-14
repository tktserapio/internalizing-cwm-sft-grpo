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
    """Deals the deck evenly between players."""
    return [deck[i::num_players] for i in range(num_players)]

def get_card_rank(card):
    """Converts a card value to its rank (A=1, K=13, Q=12, J=11)."""
    ranks = {'A': 1, 'K': 13, 'Q': 12, 'J': 11}
    return ranks.get(card.upper(), int(card))

# Required Functions
def get_initial_state():
    """Returns the initial game state before any actions are taken."""
    # Standard deck of cards
    deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4
    # Shuffle the deck
    shuffled_deck = shuffle_deck(deck)
    # Deal the deck evenly between two players
    hands = deal_cards(shuffled_deck, 2)
    # Form hands by drawing the top 3 cards from the draw pile
    hands = {i: hands[i][:3] for i in range(2)}
    # Initialize state
    state = {
        'current_player': 0,
        'hands': hands,
        'public_revealed_cards': [],
        'win_piles': {0: [], 1: []},
        'draw_piles': {0: shuffled_deck[:len(hands[0])], 1: shuffled_deck[len(hands[0]):]},
        'terminal': False
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    if action.startswith('play:'):
        card = action.split(':')[1]
        player_id = state['current_player']
        if card not in state['hands'][player_id]:
            raise ValueError(f"Invalid card '{card}' played.")
        
        # Get the opponent's card
        opponent_card = state['hands'][1 - player_id][0]
        opponent_rank = get_card_rank(opponent_card)
        
        # Determine the winner of the battle
        if get_card_rank(card) > get_card_rank(opponent_card):
            state['win_piles'][player_id].append(card)
            state['win_piles'][1 - player_id].append(opponent_card)
            state['public_revealed_cards'].append(card)
            state['public_revealed_cards'].append(opponent_card)
            state['hands'][player_id].append(card)
            state['hands'][player_id].append(opponent_card)
            state['hands'][1 - player_id].pop(0)
            state['current_player'] = 1 - player_id
        else:
            state['win_piles'][1 - player_id].append(opponent_card)
            state['win_piles'][player_id].append(card)
            state['public_revealed_cards'].append(opponent_card)
            state['public_revealed_cards'].append(card)
            state['hands'][1 - player_id].pop(0)
            state['hands'][player_id].append(opponent_card)
            state['hands'][player_id].append(card)
            state['current_player'] = 1 - player_id
        
        # Draw new cards
        state['draw_piles'][player_id].extend(state['hands'][player_id][-2:])
        state['hands'][player_id] = state['hands'][player_id][:-2]
        state['hands'][player_id].extend(state['draw_piles'][player_id])
        state['draw_piles'][player_id] = []
        
        # Check for terminal state
        if len(state['hands'][0]) == 0 or len(state['hands'][1]) == 0:
            state['terminal'] = True
        elif len(state['draw_piles'][0]) == 0 or len(state['draw_piles'][1]) == 0:
            state['terminal'] = True
        
        return state
    else:
        raise ValueError("Invalid action format.")

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['terminal']:
        if len(state['win_piles'][0]) > len(state['win_piles'][1]):
            return [1.0, 0.0]
        elif len(state['win_piles'][0]) < len(state['win_piles'][1]):
            return [0.0, 1.0]
        else:
            return [0.5, 0.5]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['terminal']:
        return []
    else:
        return ['play:' + card for card in state['hands'][state['current_player']]]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        'current_hand': state['hands'][0],
        'public_revealed_cards': state['public_revealed_cards'],
        'win_pile': state['win_piles'][0],
        'draw_pile': state['draw_piles'][0]
    }
    player_1_obs = {
        'current_hand': state['hands'][1],
        'public_revealed_cards': state['public_revealed_cards'],
        'win_pile': state['win_piles'][1],
        'draw_pile': state['draw_piles'][1]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # For simplicity, we will just randomly sample actions from the legal actions.
    # This is a placeholder function and should be expanded based on the specific requirements.
    legal_actions = get_legal_actions(resample_history.get_initial_state())
    return [random.choice(legal_actions) for _ in obs_action_history]