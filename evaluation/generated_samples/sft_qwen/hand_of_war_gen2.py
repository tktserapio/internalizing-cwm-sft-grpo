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
    """Deals cards evenly between players."""
    return [deck[i::num_players] for i in range(num_players)]

def form_hands(hand):
    """Each player draws the top three cards from their draw pile."""
    return [hand[:3], hand[3:]]

def get_card_rank(card):
    """Converts card value to its rank (A=1, K=13, Q=12, J=11)."""
    ranks = {'A': 1, 'K': 13, 'Q': 12, 'J': 11}
    return ranks.get(card.upper(), int(card))

def convert_to_action_string(card):
    """Converts card value to action string."""
    return f"play:{card}"

def get_initial_state():
    """Returns the initial game state before any actions are taken."""
    # Standard deck of cards
    deck = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'] * 4
    # Shuffle the deck
    shuffled_deck = shuffle_deck(deck)
    # Deal the deck evenly between two players
    player0_hand, player1_hand = deal_cards(shuffled_deck, 2)
    # Form hands
    player0_hand, player1_hand = form_hands(player0_hand), form_hands(player1_hand)
    # Initial state
    state = {
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'player0_win_pile': [],
        'player1_win_pile': [],
        'current_player': 0,
        'public_revealed_cards': []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Check if the action is a chance action
    if action.startswith("deal"):
        # Deal cards
        cards_to_deal = action.split(",")[-1]
        for player_hand in [state['player0_hand'], state['player1_hand']]:
            for card in cards_to_deal:
                player_hand.append(card)
        return state
    
    # Parse the action
    player_id, card = action.split(":")[1], action.split(":")[2]
    player_id = int(player_id)
    
    # Get the current player's hand
    current_hand = state[f'player{player_id}_hand']
    
    # Remove the selected card from the hand
    current_hand.remove(card)
    
    # Determine the opponent's hand
    opponent_hand = state[f'player{(player_id + 1) % 2}_hand']
    
    # Determine the opponent's card
    opponent_card = opponent_hand.pop(0)
    
    # Determine the winner of the battle
    if get_card_rank(card) > get_card_rank(opponent_card):
        # Player 0 wins
        state[f'player0_win_pile'].append(card)
        state[f'player0_win_pile'].append(opponent_card)
    else:
        # Player 1 wins
        state[f'player1_win_pile'].append(opponent_card)
        state[f'player1_win_pile'].append(card)
    
    # Draw new cards
    state[f'player{player_id}_hand'].extend(current_hand)
    
    # Update the current player
    state['current_player'] = (player_id + 1) % 2
    
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # Calculate the number of cards in each player's win pile
    player0_cards = len(state['player0_win_pile'])
    player1_cards = len(state['player1_win_pile'])
    
    # Determine the winner based on the number of cards in the win piles
    if player0_cards > player1_cards:
        return [1.0, 0.0]
    elif player1_cards > player0_cards:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    # Check if the game is over
    if len(state['player0_hand']) == 0 or len(state['player1_hand']) == 0:
        return []
    
    # Get the current player's hand
    current_hand = state[f'player{get_current_player(state)}_hand']
    
    # Get the opponent's hand
    opponent_hand = state[f'player{(get_current_player(state) + 1) % 2}_hand']
    
    # Get the public revealed cards
    public_revealed_cards = state['public_revealed_cards']
    
    # Get the current player's possible actions
    player_actions = []
    for card in current_hand:
        if card not in public_revealed_cards:
            player_actions.append(convert_to_action_string(card))
    
    return player_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    # Get the current player's hand
    current_hand = state[f'player{get_current_player(state)}_hand']
    
    # Get the opponent's hand
    opponent_hand = state[f'player{(get_current_player(state) + 1) % 2}_hand']
    
    # Get the public revealed cards
    public_revealed_cards = state['public_revealed_cards']
    
    # Get the current player's observation
    player0_obs = {
        'hand': current_hand,
        'opponent_hand': opponent_hand,
        'public_revealed_cards': public_revealed_cards
    }
    
    # Get the opponent's observation
    player1_obs = {
        'hand': opponent_hand,
        'opponent_hand': current_hand,
        'public_revealed_cards': public_revealed_cards
    }
    
    return [player0_obs, player1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement the logic to sample a valid sequence of actions.
    # For simplicity, we will just return a fixed sequence of actions.
    # In a real implementation, this would involve sampling from the policy distribution.
    # Here, we will return a fixed sequence of actions for demonstration purposes.
    actions = []
    for obs, action in obs_action_history:
        if action is None:
            # Chance action
            actions.append(f"deal:{random.choice(['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'])}")
        else:
            # Play action
            actions.append(action)
    return actions