import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def shuffle_deck(deck: List[int]) -> List[int]:
    """Shuffles the deck."""
    random.shuffle(deck)
    return deck

def deal_cards(deck: List[int], num_players: int, num_cards_per_player: int) -> Tuple[List[int], List[int]]:
    """Deals the deck evenly between two players."""
    shuffled_deck = shuffle_deck(deck)
    player0_cards = shuffled_deck[:num_cards_per_player]
    player1_cards = shuffled_deck[num_cards_per_player:num_cards_per_player * 2]
    return player0_cards, player1_cards

def form_hands(player0_cards: List[int], player1_cards: List[int]) -> Tuple[List[int], List[int]]:
    """Each player draws the top three cards from their draw pile."""
    player0_hand = player0_cards[:3]
    player1_hand = player1_cards[:3]
    return player0_hand, player1_hand

def declare_winner(state: State) -> int:
    """Determines the winner based on the game end conditions."""
    player0_win_pile = state['player0_win_pile']
    player1_win_pile = state['player1_win_pile']
    
    if len(player0_win_pile) > len(player1_win_pile):
        return 0
    elif len(player1_win_pile) > len(player0_win_pile):
        return 1
    else:
        return -1  # Draw

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = list(range(1, 17))  # Deck contains Aces through 6s
    player0_cards, player1_cards = deal_cards(deck, 2, 8)
    player0_hand, player1_hand = form_hands(player0_cards, player1_cards)
    state = {
        'player0_cards': player0_cards,
        'player1_cards': player1_cards,
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'player0_win_pile': [],
        'player1_win_pile': [],
        'current_player': 0,
        'publicly_revealed_cards': []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if action.startswith('play:'):
        card_value = int(action.split(':')[1])
        if card_value <= 6:
            new_state['publicly_revealed_cards'].append(card_value)
            if new_state['current_player'] == 0:
                new_state['player0_hand'].remove(card_value)
                new_state['player1_hand'].append(card_value)
                new_state['player0_win_pile'].append(card_value)
            else:
                new_state['player1_hand'].remove(card_value)
                new_state['player0_hand'].append(card_value)
                new_state['player1_win_pile'].append(card_value)
            new_state['current_player'] = (new_state['current_player'] + 1) % 2
        else:
            raise ValueError(f"Invalid card value: {card_value}")
    elif action.startswith('deal:'):
        cards_to_deal = action.split(',')[1:]
        new_state['player0_cards'] += cards_to_deal
        new_state['player1_cards'] += cards_to_deal
        new_state['player0_hand'], new_state['player1_hand'] = form_hands(new_state['player0_cards'], new_state['player1_cards'])
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
    else:
        raise ValueError(f"Unknown action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['player0_win_pile'] + state['player1_win_pile'] >= 16:
        return -4  # Terminal state
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    player0_win_pile = state['player0_win_pile']
    player1_win_pile = state['player1_win_pile']
    if len(player0_win_pile) > len(player1_win_pile):
        return [1.0, 0.0]
    elif len(player1_win_pile) > len(player0_win_pile):
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if get_current_player(state) == -4:
        return []
    player0_hand = state['player0_hand']
    player1_hand = state['player1_hand']
    legal_actions = ['play:' + str(card) for card in player0_hand + player1_hand]
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player0_obs = {
        'deck': state['player0_cards'],
        'hand': state['player0_hand'],
        'win_pile': state['player0_win_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    player1_obs = {
        'deck': state['player1_cards'],
        'hand': state['player1_hand'],
        'win_pile': state['player1_win_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    return [player0_obs, player1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we will just return a fixed sequence of actions
    actions = ['play:3', 'play:5', 'play:2', 'play:6', 'play:4', 'play:1', 'play:9', 'play:7']
    if player_id == 0:
        return actions[:len(actions)//2]
    else:
        return actions[len(actions)//2:]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    print("Legal Actions:", get_legal_actions(initial_state))