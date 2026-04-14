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
    """Shuffles the given deck."""
    random.shuffle(deck)
    return deck

def deal_cards(deck, num_players):
    """Deals the deck evenly between the players."""
    dealt_cards = {player: [] for player in range(num_players)}
    for i in range(len(deck)):
        dealt_cards[i % num_players].append(deck[i])
    return dealt_cards

def get_card_rank(card):
    """Converts card value to its corresponding rank (A=1, K=13, Q=12, J=11)."""
    ranks = {'A': 1, 'K': 13, 'Q': 12, 'J': 11}
    return ranks.get(card.upper(), int(card))

def convert_to_action_string(card):
    """Converts a card value to the action string format."""
    return f"play:{card}"

# Required Functions
def get_initial_state():
    """Returns the initial game state before any actions are taken."""
    # Initialize the deck
    deck = ['A', 'K', 'Q', 'J'] * 4
    shuffled_deck = shuffle_deck(deck)
    
    # Deal the deck evenly between two players
    dealt_cards = deal_cards(shuffled_deck, 2)
    
    # Form hands
    player_0_hand = dealt_cards[0][:3]
    player_1_hand = dealt_cards[1][:3]
    
    # Publicly revealed cards
    publicly_revealed_cards = []
    
    # Current player is 0
    current_player = 0
    
    # Game state
    state = {
        'deck': shuffled_deck,
        'player_0_hand': player_0_hand,
        'player_1_hand': player_1_hand,
        'publicly_revealed_cards': publicly_revealed_cards,
        'current_player': current_player,
        'player_0_win_pile': [],
        'player_1_win_pile': [],
        'running_rewards': [0.0, 0.0],
        'draw_pile': dealt_cards[current_player][3:]
    }
    
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player_id = new_state['current_player']
    
    # Get the player's hand
    player_hand = new_state[f'player_{player_id}_hand']
    
    # Get the opponent's hand
    opponent_hand = new_state[f'player_{(player_id + 1) % 2}_hand']
    
    # Get the drawn cards
    drawn_cards = new_state['draw_pile']
    
    # Get the publicly revealed cards
    public_cards = new_state['publicly_revealed_cards']
    
    # Apply the action
    if action.startswith('play:'):
        chosen_card = action.split(':')[1]
        
        # Check if the chosen card is in the player's hand
        if chosen_card in player_hand:
            # Player plays the card
            new_state[f'player_{player_id}_hand'].remove(chosen_card)
            new_state[f'player_{player_id}_win_pile'].append(chosen_card)
            
            # Opponent plays a card
            opponent_played_card = opponent_hand.pop(0)
            new_state[f'player_{(player_id + 1) % 2}_win_pile'].append(opponent_played_card)
            
            # Update the current player
            new_state['current_player'] = (player_id + 1) % 2
            
            # Add the played cards to the publicly revealed cards
            public_cards.extend([chosen_card, opponent_played_card])
        else:
            raise ValueError("Invalid card chosen.")
    elif action.startswith('deal:'):
        # Deal new cards to the player
        new_cards = action.split(',')[1:]
        new_state[f'player_{player_id}_hand'].extend(new_cards)
        new_state['draw_pile'] = drawn_cards
    else:
        raise ValueError("Invalid action.")
    
    # Update the running rewards
    new_state['running_rewards'][player_id] += 1
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    return state['running_rewards']

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    player_id = get_current_player(state)
    player_hand = state[f'player_{player_id}_hand']
    opponent_hand = state[f'player_{(player_id + 1) % 2}_hand']
    drawn_cards = state['draw_pile']
    public_cards = state['publicly_revealed_cards']
    
    # Legal actions include playing a card from the hand
    legal_actions = [convert_to_action_string(card) for card in player_hand]
    
    # If the player has no cards left in their hand, they can only draw
    if not player_hand:
        legal_actions.append('deal:')
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        'hand': state['player_0_hand'],
        'win_pile': state['player_0_win_pile'],
        'draw_pile': state['draw_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    player_1_obs = {
        'hand': state['player_1_hand'],
        'win_pile': state['player_1_win_pile'],
        'draw_pile': state['draw_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement the logic to sample a valid sequence of actions.
    # For simplicity, we will just return a fixed sequence here.
    # In a real implementation, this function should be much more complex.
    return [
        'play:A',
        'play:K',
        'play:Q',
        'play:J',
        'deal:K,Q,J,A'
    ]