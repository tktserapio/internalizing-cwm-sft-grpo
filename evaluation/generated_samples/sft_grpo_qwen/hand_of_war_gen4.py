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

def deal_cards(deck: List[int], num_players: int) -> Tuple[List[int], List[int]]:
    """Deals the deck evenly between two players."""
    half_deck = len(deck) // num_players
    return deck[:half_deck], deck[half_deck:]

def form_hands(draw_pile: List[int], hands: List[List[int]]) -> None:
    """Each player draws the top three cards from their draw pile."""
    for hand in hands:
        hand.extend(draw_pile[:3])
        del draw_pile[:3]

def get_card_rank(card: int) -> int:
    """Converts card value to its rank (Ace=1, King=13, Queen=12, Jack=11)."""
    ranks = {1: 'A', 13: 'K', 12: 'Q', 11: 'J'}
    return ranks.get(card, card)

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = list(range(1, 15))  # Deck contains Aces through Kings
    draw_pile = shuffle_deck(deck)
    player_hands = [[], []]
    form_hands(draw_pile, player_hands)
    return {
        'deck': draw_pile,
        'player_hands': player_hands,
        'public_revealed_cards': [],
        'current_player': 0,
        'player_names': ['Player 0', 'Player 1'],
        'win_piles': [[], []],
        'running_rewards': [0.0, 0.0]
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    state_copy = state.copy()
    if action.startswith('play:'):
        card_value = int(action.split(':')[1])
        card_rank = get_card_rank(card_value)
        state_copy['public_revealed_cards'].append(card_rank)
        state_copy['current_player'] = (state_copy['current_player'] + 1) % 2
        return state_copy
    elif action.startswith('deal:'):
        draw_pile = state['deck']
        cards_to_deal = action.split(',')[1:]
        drawn_cards = []
        for card in cards_to_deal:
            drawn_cards.append(draw_pile.pop())
        player_hands = state['player_hands']
        player_hands[state['current_player']].extend(drawn_cards)
        return state_copy
    else:
        raise ValueError(f"Invalid action: {action}")

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return state['player_names'][player_id]

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    return state['running_rewards']

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['current_player'] == -4:
        return []
    player_hands = state['player_hands'][state['current_player']]
    public_revealed_cards = state['public_revealed_cards']
    legal_actions = []
    for card in player_hands:
        if card not in public_revealed_cards:
            legal_actions.append(f'play:{card}')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_hands = state['player_hands']
    public_revealed_cards = state['public_revealed_cards']
    player_0_obs = {
        'hand': player_hands[0],
        'public_revealed_cards': public_revealed_cards
    }
    player_1_obs = {
        'hand': player_hands[1],
        'public_revealed_cards': public_revealed_cards
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ['play:7', 'play:K', 'play:A', 'deal:7,8,9,10,K,Q,J']
    else:
        return ['play:7', 'play:K', 'play:A', 'deal:7,8,9,10,K,Q,J']