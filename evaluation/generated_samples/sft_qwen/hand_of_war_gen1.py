import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import List, Dict, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def get_deck() -> List[str]:
    """Returns a shuffled list of card ranks."""
    ranks = ['A', 'K', 'Q', 'J']
    return ranks * 4  # Assuming a standard deck of 52 cards with 4 suits

def shuffle_deck(deck: List[str]) -> List[str]:
    """Shuffles the given deck."""
    import random
    random.shuffle(deck)
    return deck

def deal_cards(deck: List[str], num_players: int) -> List[List[str]]:
    """Deals cards evenly between players."""
    half_deck = len(deck) // num_players
    return [deck[i:i+half_deck] for i in range(0, len(deck), half_deck)]

def draw_cards(hand: List[str], draw_pile: List[str]) -> List[str]:
    """Draws cards from the draw pile to replenish the hand."""
    drawn_cards = hand[:3]  # Draw 3 cards initially
    hand.clear()
    hand.extend(drawn_cards)
    hand.extend(draw_pile[:3])  # Add 3 cards from the draw pile
    draw_pile = draw_pile[3:]  # Remove the drawn cards from the draw pile
    return hand, draw_pile

def declare_war(cards: List[str]) -> List[str]:
    """Simulates a showdown when cards are of the same rank."""
    # For simplicity, we assume the player with the higher card wins
    # In a real game, this could involve more complex logic
    return cards

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = shuffle_deck(get_deck())
    players = deal_cards(deck, 2)
    state = {
        'current_player': 0,
        'draw_pile': deck,
        'win_piles': {0: [], 1: []},
        'public_revealed_cards': [],
        'hands': {0: players[0], 1: players[1]},
        'legal_actions': []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    if action.startswith('play:'):
        card_index = int(action.split(':')[1])
        current_player = state['current_player']
        hand = state['hands'][current_player]
        card = hand.pop(card_index)
        state['public_revealed_cards'].append(card)
        state['legal_actions'] = get_legal_actions(state)
        if state['legal_actions']:
            next_player = (current_player + 1) % 2
            state['current_player'] = next_player
        else:
            state['legal_actions'] = []
            state['current_player'] = -4  # Terminal state
    elif action.startswith('deal:'):
        cards_to_deal = action.split(':')[1].split(',')
        for card in cards_to_deal:
            state['draw_pile'].remove(card)
        state['legal_actions'] = get_legal_actions(state)
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['current_player'] == -4:
        return [len(state['win_piles'][0]), len(state['win_piles'][1])]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = state['current_player']
    hands = state['hands']
    public_revealed_cards = state['public_revealed_cards']
    draw_pile = state['draw_pile']
    win_piles = state['win_piles']
    
    if state['current_player'] == -4:
        return []
    
    legal_actions = []
    
    # Check if the current player can play a card
    for card_index in range(len(hands[current_player])):
        card = hands[current_player][card_index]
        if card not in public_revealed_cards:
            legal_actions.append(f'play:{card_index}')
    
    # Check if the current player can deal cards
    if len(public_revealed_cards) >= 3:
        legal_actions.append('deal:' + ','.join(public_revealed_cards))
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    current_player = state['current_player']
    hands = state['hands']
    public_revealed_cards = state['public_revealed_cards']
    
    player_0_obs = {
        'hand': hands[0],
        'public_revealed_cards': public_revealed_cards,
        'legal_actions': get_legal_actions(state),
        'win_pile': state['win_piles'][0]
    }
    
    player_1_obs = {
        'hand': hands[1],
        'public_revealed_cards': public_revealed_cards,
        'legal_actions': get_legal_actions(state),
        'win_pile': state['win_piles'][1]
    }
    
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # This function would need to be implemented based on the specific game dynamics and history.
    # For simplicity, we will just return a fixed sequence of actions.
    # In a real implementation, this would involve sampling from the possible sequences of actions that lead to the current state.
    # Here, we return a fixed sequence of actions that can explain the current state.
    # Note: This is a placeholder implementation.
    return [
        'play:0',
        'play:1',
        'play:2',
        'play:3',
        'play:4',
        'play:5',
        'play:6',
        'play:7',
        'play:8',
        'play:9',
        'play:10',
        'play:11',
        'play:12',
        'play:13',
        'play:14',
        'play:15',
        'deal:A,K,Q,J'
    ]