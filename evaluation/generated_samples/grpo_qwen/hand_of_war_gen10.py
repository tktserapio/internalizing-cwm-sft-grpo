import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initialize the game state with the deck shuffled and dealt evenly
    deck = ['A', 'K', 'Q', 'J'] * 4  # Aces, Kings, Queens, Jacks
    np.random.shuffle(deck)
    player1_cards = deck[:8]
    player2_cards = deck[8:]
    return {
        'player1_cards': player1_cards,
        'player2_cards': player2_cards,
        'current_player': 0,  # Player 0 starts first
        'public_revealed_cards': [],  # Not playable anymore
        'draw_piles': {'player1': player1_cards, 'player2': player2_cards},
        'win_piles': {'player1': [], 'player2': []}
    }

# Apply an action to the game state
def apply_action(state: State, action: Action) -> State:
    # Extract the player ID from the action
    player_id = int(action.split(':')[1])
    
    # Get the current player's cards
    current_cards = state[f'draw_piles[player{player_id}]']
    
    # Get the card to play
    card_to_play = action.split(':')[2]
    
    # Find the index of the card to play in the current player's cards
    card_index = current_cards.index(card_to_play)
    
    # Remove the card from the draw pile and add it to the win pile
    win_pile = state[f'win_piles[player{player_id}]']
    win_pile.append(current_cards.pop(card_index))
    
    # Determine the opponent's cards
    opponent_cards = state[f'draw_piles[player{(player_id + 1) % 2}]']
    
    # Determine the winner of the battle
    if card_to_play in ('A', 'K', 'Q', 'J'):
        if card_to_play > opponent_cards[card_index]:
            # Player 1 wins
            state[f'draw_piles[player{player_id}]'].extend(opponent_cards)
            state[f'draw_piles[player{(player_id + 1) % 2}]'].extend(current_cards)
        else:
            # Player 2 wins
            state[f'draw_piles[player{(player_id + 1) % 2}]'].extend(opponent_cards)
            state[f'draw_piles[player{player_id}]'].extend(current_cards)
    else:
        raise ValueError("Invalid card rank")
    
    # Update the current player
    state['current_player'] = (player_id + 1) % 2
    
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}'

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    # Calculate the number of cards in each player's win pile
    player1_win_pile = len(state['win_piles']['player1'])
    player2_win_pile = len(state['win_piles']['player2'])
    
    # Determine the winner based on the number of cards in the win piles
    if player1_win_pile > player2_win_pile:
        return [1.0, 0.0]
    elif player2_win_pile > player1_win_pile:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    # Check if the game is over
    if len(state['draw_piles']['player1']) == 0 or len(state['draw_piles']['player2']) == 0:
        return []
    
    # Get the current player's cards
    current_cards = state[f'draw_piles[player{get_current_player(state)}]']
    
    # Return the legal actions
    return [f'play:{card}' for card in current_cards]

# Get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    # Get the current player's cards
    current_cards = state[f'draw_piles[player{get_current_player(state)}]']
    
    # Create the observations
    observations = [
        {
            'cards': current_cards,
            'opponent_cards': state[f'draw_piles[player{(get_current_player(state) + 1) % 2}]'],
            'public_revealed_cards': state['public_revealed_cards']
        },
        {
            'cards': state[f'draw_piles[player{(get_current_player(state) + 1) % 2}]'],
            'opponent_cards': current_cards,
            'public_revealed_cards': state['public_revealed_cards']
        }
    ]
    
    return observations

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Implement the resampling logic here
    # This is a placeholder for the actual resampling logic
    # For simplicity, we will just return a fixed sequence of actions
    actions = []
    for obs, action in obs_action_history:
        actions.append(f'play:{obs["cards"][0]}')
    return actions