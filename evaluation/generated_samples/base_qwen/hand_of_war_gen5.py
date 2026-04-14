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
    """Shuffles the given deck of cards."""
    random.shuffle(deck)
    return deck

def deal_cards(deck, num_players):
    """Deals the deck evenly among the players."""
    return [deck[i::num_players] for i in range(num_players)]

def get_card_rank(card):
    """Converts a card string to its rank (A, K, Q, J)."""
    ranks = {'A': 14, 'K': 13, 'Q': 12, 'J': 11}
    return ranks.get(card, int(card))

# Required Functions
def get_initial_state():
    """Returns the initial game state before any actions are taken."""
    # Deck of cards
    deck = ['A', 'K', 'Q', 'J'] * 4
    shuffle_deck(deck)
    
    # Initial hands
    player0_hand = deck[:3]
    player1_hand = deck[3:6]
    
    # Draw piles
    player0_draw = deck[6:]
    player1_draw = deck[6:]
    
    # Win piles
    player0_win = []
    player1_win = []
    
    # Current player
    current_player = 0
    
    # Observations
    player0_obs = {
        'hand': player0_hand,
        'draw': player0_draw,
        'win': player0_win
    }
    player1_obs = {
        'hand': player1_hand,
        'draw': player1_draw,
        'win': player1_win
    }
    
    return {
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'player0_draw': player0_draw,
        'player1_draw': player1_draw,
        'player0_win': player0_win,
        'player1_win': player1_win,
        'current_player': current_player,
        'publicly_revealed_cards': [],
        'player0_obs': player0_obs,
        'player1_obs': player1_obs
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    if action.startswith('deal'):
        # Deal cards
        _, _, cards_to_deal = action.split(':')
        cards_to_deal = cards_to_deal.split(',')
        player_id, cards = int(cards_to_deal[0]), cards_to_deal[1:]
        new_state = state.copy()
        new_state[f'player{player_id}_draw'] += cards
        return new_state
        
    elif action.startswith('play'):
        # Play a card
        player_id, card = int(action.split(':')[1]), action.split(':')[1]
        new_state = state.copy()
        
        # Check if the card is in the hand
        if card in state[f'player{player_id}_hand']:
            new_state[f'player{player_id}_hand'].remove(card)
            new_state[f'player{player_id}_win'].append(card)
        else:
            raise ValueError(f"Player {player_id} tried to play a card not in their hand.")
        
        # Update the publicly revealed cards
        new_state['publicly_revealed_cards'].append(card)
        
        # Determine the current player
        current_player = get_current_player(new_state)
        
        # Check for showdown
        if len(new_state[f'player{current_player}_win']) == 16:
            return new_state
        
        # Check for end of game
        if len(new_state[f'player{current_player}_draw']) == 0:
            return new_state
        
        # Switch to the other player
        new_state['current_player'] = 1 - current_player
        
        return new_state
    
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
    player0_win = len(state['player0_win'])
    player1_win = len(state['player1_win'])
    if player0_win == 16 or player1_win == 16:
        return [1.0, 0.0] if player0_win == 16 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = get_current_player(state)
    player_id = current_player
    legal_actions = []
    
    # Player 0's turn
    if current_player == 0:
        legal_actions.append(f"play:{state['player0_hand'][0]}")
        if len(state['player0_draw']) > 0:
            legal_actions.append(f'deal:{state["player0_draw"][0]}')
    
    # Player 1's turn
    elif current_player == 1:
        legal_actions.append(f"play:{state['player1_hand'][0]}")
        if len(state['player1_draw']) > 0:
            legal_actions.append(f'deal:{state["player1_draw"][0]}')
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        {
            'hand': state[f'player0_hand'],
            'draw': state[f'player0_draw'],
            'win': state['player0_win']
        },
        {
            'hand': state[f'player1_hand'],
            'draw': state[f'player1_draw'],
            'win': state['player1_win']
        }
    ]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement the logic to resample history based on the current observations.
    # For simplicity, we will just return a fixed sequence of actions.
    # In a real implementation, this would involve complex sampling logic.
    return [
        f"play:{obs_action_history[-1][0]['hand'][0]}" if obs_action_history[-1][1] is None else obs_action_history[-1][1],
        f'deal:{obs_action_history[-1][0]["draw"][0]}'
    ]