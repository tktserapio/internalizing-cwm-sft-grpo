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

# Helper functions
def parse_deck(deck: List[int]) -> List[int]:
    """Helper function to parse the deck into a list of integers for easier comparison."""
    return list(range(1, len(deck) + 1))

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initialize the deck
    deck = list(range(1, 17))
    # Shuffle the deck
    import random
    random.shuffle(deck)
    
    # Deal the deck evenly between two players
    player1_cards = deck[:8]
    player2_cards = deck[8:]
    
    # Form hands
    player1_hand = player1_cards[:3]
    player2_hand = player2_cards[:3]
    
    # Initialize state
    state = {
        "deck": deck,
        "player1_hand": player1_hand,
        "player2_hand": player2_hand,
        "player1_win_pile": [],
        "player2_win_pile": [],
        "current_player": 0,
        "publicly_revealed_cards": []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    if action.startswith("play:"):
        card_value = int(action.split(":")[1])
        if card_value > 0 and card_value <= 16:
            new_state[action] = card_value
            new_state["publicly_revealed_cards"].append(card_value)
            new_state["current_player"] = (new_state["current_player"] + 1) % 2
            return new_state
    elif action.startswith("deal:"):
        dealt_cards = action.split(",")[:-1]
        new_state["deck"] = parse_deck(dealt_cards)
        new_state["player1_hand"] = parse_deck(dealt_cards[:8])
        new_state["player2_hand"] = parse_deck(dealt_cards[8:])
        new_state["current_player"] = 0
        return new_state
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    player1_win_pile = len(state["player1_win_pile"])
    player2_win_pile = len(state["player2_win_pile"])
    if player1_win_pile == 16 or player2_win_pile == 16:
        return [1.0, 0.0] if player1_win_pile == 16 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = get_current_player(state)
    if current_player == -4:
        return []
    player_hand = state[f"player{current_player+1}_hand"]
    if player_hand:
        return ["play:" + str(card) for card in player_hand]
    else:
        return ["deal:" + ",".join(str(card) for card in state[f"player{current_player+1}_hand"])]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player1_hand = state["player1_hand"]
    player2_hand = state["player2_hand"]
    player1_publicly_revealed_cards = state["publicly_revealed_cards"][:len(player1_hand)]
    player2_publicly_revealed_cards = state["publicly_revealed_cards"][len(player1_hand):len(player1_hand) + len(player2_hand)]
    player1_observation = {
        "hand": player1_hand,
        "revealed_cards": player1_publicly_revealed_cards
    }
    player2_observation = {
        "hand": player2_hand,
        "revealed_cards": player2_publicly_revealed_cards
    }
    return [player1_observation, player2_observation]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to be implemented based on the specific game logic and history.
    # For simplicity, we will return a dummy sequence here.
    # In a real implementation, this function would randomly sample actions that lead to the given observations.
    return ["play:1", "play:2", "play:3", "deal:1,2,3,4,5,6,7,8", "play:9", "play:10", "play:11", "play:12", "play:13", "play:14", "play:15", "play:16"]