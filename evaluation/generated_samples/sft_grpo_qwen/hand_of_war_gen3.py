import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper functions
def shuffle_deck(deck: List[int]) -> List[int]:
    """Shuffles the deck."""
    random.shuffle(deck)
    return deck

def deal_cards(deck: List[int], num_players: int) -> Tuple[List[int], List[int]]:
    """Deals cards evenly between players."""
    half_deck = len(deck) // num_players
    return (deck[:half_deck], deck[half_deck:])

def form_hands(deck: List[int], hands: List[List[int]]) -> None:
    """Each player draws the top three cards from their draw pile."""
    for hand in hands:
        hand.extend(deck[:3])
        del deck[:3]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = list(range(1, 17)) * 2  # Create a shuffled deck with duplicates
    hands = [[] for _ in range(2)]
    return {
        "deck": deck,
        "hands": hands,
        "public_revealed_cards": [],
        "current_player": 0,
        "player_names": ["Player 0", "Player 1"],
        "win_piles": [0, 0],
        "draw_piles": [deck, deck]
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    if action.startswith("play:"):
        card_index = int(action.split(":")[1])
        new_state["public_revealed_cards"].append(card_index)
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
        if new_state["current_player"] == 0:
            new_state["draw_piles"][0].extend(new_state["deck"])
            new_state["deck"] = []
        else:
            new_state["draw_piles"][1].extend(new_state["deck"])
            new_state["deck"] = []
        new_state["hands"][new_state["current_player"]].pop(0)
    elif action.startswith("deal:"):
        new_state["deck"] = shuffle_deck(list(map(int, action.split(",")[:-1])))
        form_hands(new_state["deck"], new_state["hands"])
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return state["player_names"][player_id]

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    return [state["win_piles"][0], state["win_piles"][1]]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["deck"]:
        return ["play:" + str(card) for card in state["hands"][state["current_player"]]]
    elif state["draw_piles"][state["current_player"]]:
        return ["deal:" + ",".join(map(str, state["draw_piles"][state["current_player"]][:3]))]
    else:
        return []

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        "deck": state["deck"],
        "hands": state["hands"][0],
        "public_revealed_cards": state["public_revealed_cards"]
    }
    player_1_obs = {
        "deck": state["deck"],
        "hands": state["hands"][1],
        "public_revealed_cards": state["public_revealed_cards"]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # This function would need to be implemented based on the specific game logic and history.
    # For simplicity, we will just return a random legal action.
    legal_actions = get_legal_actions(resample_history.get_observations(resample_history.state))
    return [random.choice(legal_actions)]