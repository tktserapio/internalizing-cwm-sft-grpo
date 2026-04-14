import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import List, Dict, Any, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the state
def get_initial_state() -> State:
    # Initial state setup
    state = {
        "deck": ["A", "K", "Q", "J", "A", "K", "Q", "J", "A", "K", "Q", "J", "A", "K", "Q", "J"],
        "draw_piles": [{"top_card": "A"}, {"top_card": "A"}],
        "win_piles": [{"cards": []}, {"cards": []}],
        "current_player": 0,
        "publicly_revealed_cards": [],
        "obs_action_history": []
    }
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action.startswith("play:"):
        new_state = handle_play_action(new_state, action)
    elif action.startswith("deal:"):
        new_state = handle_deal_action(new_state, action)
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

# Handle play action
def handle_play_action(state: State, action: Action) -> State:
    player_id = state["current_player"]
    card_to_play = action.split(":")[1]
    state["publicly_revealed_cards"].append(card_to_play)
    state["draw_piles"][player_id]["top_card"] = state["deck"].pop(0)
    state["current_player"] = (player_id + 1) % 2
    return state

# Handle deal action
def handle_deal_action(state: State, action: Action) -> State:
    # This is a placeholder for the actual deal logic which would involve shuffling and dealing cards
    # For simplicity, we just simulate a deal here
    state["deck"] = sorted(state["deck"])
    for i in range(3):
        state["draw_piles"][state["current_player"]]["top_card"] = state["deck"].pop(0)
    state["current_player"] = (state["current_player"] + 1) % 2
    return state

# Get current player
def get_current_player(state: State) -> int:
    return state["current_player"]

# Get player name
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards
def get_rewards(state: State) -> List[float]:
    # Simple reward system based on win pile size
    player0_win_pile = len(state["win_piles"][0]["cards"])
    player1_win_pile = len(state["win_piles"][1]["cards"])
    return [player0_win_pile, player1_win_pile]

# Get legal actions
def get_legal_actions(state: State) -> List[Action]:
    player_id = get_current_player(state)
    if player_id == -4:
        return []  # Terminal state
    if state["draw_piles"][player_id]["top_card"] is None:
        return []  # Draw pile depleted
    return ["play:" + card for card in state["draw_piles"][player_id]["top_card"]]

# Get observations
def get_observations(state: State) -> List[PlayerObservation]:
    player0_obs = {
        "publicly_revealed_cards": state["publicly_revealed_cards"],
        "deck": state["deck"],
        "draw_piles": state["draw_piles"],
        "win_piles": state["win_piles"],
        "current_player": get_current_player(state),
        "publicly_revealed_cards": state["publicly_revealed_cards"]
    }
    player1_obs = {
        "publicly_revealed_cards": state["publicly_revealed_cards"],
        "deck": state["deck"],
        "draw_piles": state["draw_piles"],
        "win_piles": state["win_piles"],
        "current_player": get_current_player(state),
        "publicly_revealed_cards": state["publicly_revealed_cards"]
    }
    return [player0_obs, player1_obs]

# Resample history
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Placeholder for resampling logic
    # For simplicity, we just return a random legal action
    legal_actions = get_legal_actions(resample_history.get_initial_state())
    return [legal_actions[i % len(legal_actions)] for i in range(len(obs_action_history))]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    action = "play:A"
    new_state = apply_action(initial_state, action)
    print("New State after play:A:", new_state)