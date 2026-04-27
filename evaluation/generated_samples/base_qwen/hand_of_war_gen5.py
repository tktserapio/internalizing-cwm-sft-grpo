import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initialize the deck and deal the cards
    deck = ['A', 'K', 'Q', 'J'] * 4  # Aces, Kings, Queens, Jacks
    shuffled_deck = deck[:]
    import random
    random.shuffle(shuffled_deck)
    
    # Shuffle and deal the deck evenly between two players
    player0_cards = shuffled_deck[:8]
    player1_cards = shuffled_deck[8:]
    
    # Form hands by drawing the top 3 cards
    player0_hand = player0_cards[:3]
    player1_hand = player1_cards[:3]
    
    # Initial state dictionary
    state = {
        'deck': shuffled_deck,
        'player0_hand': player0_hand,
        'player1_hand': player1_hand,
        'player0_win_pile': [],
        'player1_win_pile': [],
        'player0_draw_pile': player0_cards[3:],
        'player1_draw_pile': player1_cards[3:],
        'current_player': 0,
        'publicly_revealed_cards': []
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    if action.startswith('play:'):
        card_index = int(action.split(':')[1])
        if card_index < len(state['player0_hand']):
            # Player 0 plays a card
            state['player0_hand'][card_index], state['publicly_revealed_cards'] = state['publicly_revealed_cards'], state['player0_hand'][card_index]
            state['player0_hand'][card_index] = None
            state['current_player'] = 1
        else:
            raise ValueError("Invalid card index")
    elif action.startswith('deal:'):
        # Not implemented in this version
        pass
    else:
        raise ValueError("Unknown action")
    
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards per player
def get_rewards(state: State) -> List[float]:
    # Reward system not implemented here
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    player_id = get_current_player(state)
    if player_id == 0:
        return ['play:0', 'play:1', 'play:2']
    else:
        return ['play:0', 'play:1', 'play:2']

# Get observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    player0_obs = {
        'hand': state['player0_hand'],
        'win_pile': state['player0_win_pile'],
        'draw_pile': state['player0_draw_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    player1_obs = {
        'hand': state['player1_hand'],
        'win_pile': state['player1_win_pile'],
        'draw_pile': state['player1_draw_pile'],
        'publicly_revealed_cards': state['publicly_revealed_cards']
    }
    return [player0_obs, player1_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Placeholder for resampling logic
    # For simplicity, we just return the last action
    return [obs_action_history[-1][1]] if obs_action_history else []

# Example usage
if __name__ == "__main__":
    state = get_initial_state()
    print(state)
    
    # Apply some actions
    state = apply_action(state, 'play:0')
    state = apply_action(state, 'play:1')
    state = apply_action(state, 'play:2')
    
    print(state)