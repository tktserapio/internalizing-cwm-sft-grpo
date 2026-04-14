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

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initial state setup
    state = {
        "deck": ["A", "K", "Q", "J", "A", "K", "Q", "J", "A", "K", "Q", "J", "A", "K", "Q", "J"],
        "draw_piles": [{"cards": ["A", "K", "Q", "J"], "empty": False}, {"cards": ["A", "K", "Q", "J"], "empty": False}],
        "win_piles": [{"cards": [], "empty": False}, {"cards": [], "empty": False}],
        "current_player": 0,
        "public_revealed_cards": [],
        "obs_action_history": []
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action.startswith("play:"):
        card_index = int(action.split(":")[1])
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
        new_state["public_revealed_cards"].append(action)
        new_state["draw_piles"][new_state["current_player"]]["cards"].pop(card_index)
        new_state["win_piles"][new_state["current_player"]]["cards"].extend([state["deck"].pop(card_index)])
    elif action.startswith("deal:"):
        deal_cards = action.split(",")[1:]
        new_state["deck"] = deal_cards
        new_state["draw_piles"][new_state["current_player"]]["cards"] = deal_cards
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state["current_player"]

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    # Rewards are not tracked in this simplified version
    return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    current_player = state["current_player"]
    public_revealed_cards = state["public_revealed_cards"]
    draw_piles = state["draw_piles"][current_player]["cards"]
    win_piles = state["win_piles"][current_player]["cards"]
    deck = state["deck"]
    obs_action_history = state["obs_action_history"]
    
    legal_actions = []
    if len(draw_piles) > 0:
        legal_actions.append(f"play:{draw_piles.index(public_revealed_cards[-1])}")
    if len(deck) > 0:
        legal_actions.append("deal:" + ",".join(deck))
    return legal_actions

# Get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    current_player = state["current_player"]
    public_revealed_cards = state["public_revealed_cards"]
    draw_piles = state["draw_piles"][current_player]["cards"]
    win_piles = state["win_piles"][current_player]["cards"]
    obs = {
        "deck": state["deck"],
        "draw_piles": draw_piles,
        "win_piles": win_piles,
        "public_revealed_cards": public_revealed_cards,
        "obs_action_history": state["obs_action_history"]
    }
    return [obs, obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would typically involve sampling actions based on the history
    # For simplicity, we just return a fixed sequence of actions
    return [
        "play:0",
        "play:1",
        "play:2",
        "play:3",
        "deal:A,K,Q,J",
        "play:0",
        "play:1",
        "play:2",
        "play:3",
        "deal:A,K,Q,J",
        "play:0",
        "play:1",
        "play:2",
        "play:3",
        "deal:A,K,Q,J",
        "play:0",
        "play:1",
        "play:2",
        "play:3",
        "deal:A,K,Q,J",
        "play:0",
        "play:1",
        "play:2",
        "play:3",
        "deal:A,K,Q,J"
    ]