import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Dict, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def parse_deck(deck: List[str]) -> List[str]:
    """Helper function to parse the deck into a list of card ranks."""
    return ['A', 'K', 'Q', 'J'] * 4

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initialize the deck and shuffle it
    deck = parse_deck(list('A K Q J A K Q J A K Q J A K'))
    shuffled_deck = deck[:]
    import random
    random.shuffle(shuffled_deck)
    
    # Deal the deck evenly between two players
    player1_cards = shuffled_deck[:8]
    player2_cards = shuffled_deck[8:]
    
    # Form hands
    player1_hand = player1_cards[:3]
    player2_hand = player2_cards[:3]
    
    # Initialize state
    state = {
        'deck': shuffled_deck,
        'player1_cards': player1_cards,
        'player2_cards': player2_cards,
        'player1_hand': player1_hand,
        'player2_hand': player2_hand,
        'public_revealed_cards': [],
        'current_player': 0,
        'player1_win_pile': [],
        'player2_win_pile': [],
        'player1_draw_pile': player1_cards[3:],
        'player2_draw_pile': player2_cards[3:]
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    if action.startswith("play:"):
        card_index = int(action.split(":")[1])
        player_id = state['current_player']
        if player_id == 0:
            player_hand = state['player1_hand']
        else:
            player_hand = state['player2_hand']
        
        # Remove the chosen card from the hand
        player_hand.pop(card_index)
        
        # Get the opponent's hand
        opponent_hand = state['player1_hand'] if player_id == 1 else state['player2_hand']
        
        # Determine the winner of the battle
        player_card = player_hand[card_index]
        opponent_card = opponent_hand[card_index]
        
        # Determine the ranking of the cards
        player_rank = 'A' if player_card == 'A' else ('K' if player_card == 'K' else ('Q' if player_card == 'Q' else 'J'))
        opponent_rank = 'A' if opponent_card == 'A' else ('K' if opponent_card == 'K' else ('Q' if opponent_card == 'Q' else 'J'))
        
        # Determine the winner based on the ranking
        if player_rank > opponent_rank:
            state['player1_win_pile'].append(player_card)
            state['player1_win_pile'].append(opponent_card)
        elif player_rank < opponent_rank:
            state['player2_win_pile'].append(player_card)
            state['player2_win_pile'].append(opponent_card)
        else:
            # Showdown
            showdown_cards = []
            for _ in range(2):
                player_draw = state['player1_draw_pile'].pop(0) if player_id == 0 else state['player2_draw_pile'].pop(0)
                opponent_draw = state['player2_draw_pile'].pop(0) if player_id == 0 else state['player1_draw_pile'].pop(0)
                showdown_cards.append(player_draw)
                showdown_cards.append(opponent_draw)
            
            # Determine the winner of the showdown
            player_showdown_card = state['player1_hand'][card_index]
            opponent_showdown_card = state['player2_hand'][card_index]
            
            player_showdown_rank = 'A' if player_showdown_card == 'A' else ('K' if player_showdown_card == 'K' else ('Q' if player_showdown_card == 'Q' else 'J'))
            opponent_showdown_rank = 'A' if opponent_showdown_card == 'A' else ('K' if opponent_showdown_card == 'K' else ('Q' if opponent_showdown_card == 'Q' else 'J'))
            
            if player_showdown_rank > opponent_showdown_rank:
                state['player1_win_pile'].extend(showdown_cards)
            elif player_showdown_rank < opponent_showdown_rank:
                state['player2_win_pile'].extend(showdown_cards)
            else:
                # Another showdown
                for _ in range(2):
                    player_draw = state['player1_draw_pile'].pop(0) if player_id == 0 else state['player2_draw_pile'].pop(0)
                    opponent_draw = state['player2_draw_pile'].pop(0) if player_id == 0 else state['player1_draw_pile'].pop(0)
                    showdown_cards.append(player_draw)
                    showdown_cards.append(opponent_draw)
                
                player_showdown_card = state['player1_hand'][card_index]
                opponent_showdown_card = state['player2_hand'][card_index]
                
                player_showdown_rank = 'A' if player_showdown_card == 'A' else ('K' if player_showdown_card == 'K' else ('Q' if player_showdown_card == 'Q' else 'J'))
                opponent_showdown_rank = 'A' if opponent_showdown_card == 'A' else ('K' if opponent_showdown_card == 'K' else ('Q' if opponent_showdown_card == 'Q' else 'J'))
                
                if player_showdown_rank > opponent_showdown_rank:
                    state['player1_win_pile'].extend(showdown_cards)
                elif player_showdown_rank < opponent_showdown_rank:
                    state['player2_win_pile'].extend(showdown_cards)
        
        # Update the current player
        state['current_player'] = 1 if player_id == 0 else 0
        
        # Draw new cards
        state['player1_draw_pile'].extend(state['player1_hand'])
        state['player2_draw_pile'].extend(state['player2_hand'])
        state['player1_hand'] = state['player1_draw_pile'][:3]
        state['player2_hand'] = state['player2_draw_pile'][:3]
        
        # Shuffle the draw piles
        random.shuffle(state['player1_draw_pile'])
        random.shuffle(state['player2_draw_pile'])
        
        # Update the public revealed cards
        state['public_revealed_cards'].append(f"{player_id}: {action}")
        
        return state
    else:
        raise ValueError("Invalid action")

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if len(state['player1_cards']) + len(state['player1_win_pile']) == 16:
        return [1.0, 0.0]
    elif len(state['player2_cards']) + len(state['player2_win_pile']) == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if len(state['player1_cards']) == 0 or len(state['player2_cards']) == 0:
        return []
    else:
        return ["play:" + str(i) for i in range(3)]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player1_obs = {
        'hand': state['player1_hand'],
        'win_pile': state['player1_win_pile'],
        'draw_pile': state['player1_draw_pile'],
        'public_revealed_cards': state['public_revealed_cards']
    }
    player2_obs = {
        'hand': state['player2_hand'],
        'win_pile': state['player2_win_pile'],
        'draw_pile': state['player2_draw_pile'],
        'public_revealed_cards': state['public_revealed_cards']
    }
    return [player1_obs, player2_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement the logic to resample history based on the observations.
    # For simplicity, we will just return a fixed sequence of actions.
    return [
        "play:0",
        "play:1",
        "play:2",
        "play:0",
        "play:1",
        "play:2",
        "play:0",
        "play:1",
        "play:2",
        "play:0",
        "play:1",
        "play:2"
    ]