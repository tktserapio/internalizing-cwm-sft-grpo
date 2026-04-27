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

# Helper function to create a shuffled deck
def create_deck() -> List[int]:
    ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]  # 11=Ace, 12=King, 13=Queen, 14=Jack
    random.shuffle(ranks)
    return ranks

# Initial state function
def get_initial_state() -> State:
    deck = create_deck()
    player0_hand = deck[:3]
    player1_hand = deck[3:6]
    player0_draw_pile = deck[6:]
    player1_draw_pile = deck[6:]
    
    return {
        "player0_hand": player0_hand,
        "player1_hand": player1_hand,
        "player0_draw_pile": player0_draw_pile,
        "player1_draw_pile": player1_draw_pile,
        "player0_win_pile": [],
        "player1_win_pile": [],
        "current_player": 0,
        "publicly_revealed_cards": []
    }

# Apply action function
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action.startswith("play:"):
        card_index = int(action.split(":")[1])
        new_state["current_player"] = (new_state["current_player"] + 1) % 2
        new_state[action[5:]] = state[action[5:]].pop(card_index)
        new_state["publicly_revealed_cards"].append(action[5:])
        if len(state[action[5:]]) == 0:
            new_state["current_player"] = (new_state["current_player"] + 1) % 2
    elif action.startswith("deal:"):
        cards_to_deal = action.split(",")[:3]
        for i in range(3):
            new_state["player0_draw_pile"][i], new_state["player1_draw_pile"][i] = new_state["player1_draw_pile"][i], new_state["player0_draw_pile"][i]
    return new_state

# Get current player function
def get_current_player(state: State) -> int:
    return state["current_player"]

# Get player name function
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get rewards function
def get_rewards(state: State) -> list[float]:
    player0_win_pile = len(state["player0_win_pile"])
    player1_win_pile = len(state["player1_win_pile"])
    if player0_win_pile > player1_win_pile:
        return [1.0, 0.0]
    elif player1_win_pile > player0_win_pile:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]

# Get legal actions function
def get_legal_actions(state: State) -> list[Action]:
    current_player = get_current_player(state)
    player0_hand = state["player0_hand"]
    player1_hand = state["player1_hand"]
    player0_draw_pile = state["player0_draw_pile"]
    player1_draw_pile = state["player1_draw_pile"]
    
    legal_actions = []
    if current_player == 0:
        legal_actions.append(f"play:{state['player0_hand'].index(max(state['player0_hand']))}")
        if len(player0_draw_pile) > 0:
            legal_actions.append("deal:")
            for card in player0_draw_pile:
                legal_actions.append(f"{card},")
            legal_actions[-1] = legal_actions[-1][:-1]  # Remove last comma
    else:
        legal_actions.append(f"play:{state['player1_hand'].index(max(state['player1_hand']))}")
        if len(player1_draw_pile) > 0:
            legal_actions.append("deal:")
            for card in player1_draw_pile:
                legal_actions.append(f"{card},")
            legal_actions[-1] = legal_actions[-1][:-1]  # Remove last comma
    
    return legal_actions

# Get observations function
def get_observations(state: State) -> list[PlayerObservation]:
    player0_hand = state["player0_hand"]
    player1_hand = state["player1_hand"]
    player0_win_pile = state["player0_win_pile"]
    player1_win_pile = state["player1_win_pile"]
    player0_publicly_revealed_cards = state["publicly_revealed_cards"]
    player1_publicly_revealed_cards = state["publicly_revealed_cards"]
    
    player0_observation = {
        "hand": player0_hand,
        "win_pile": player0_win_pile,
        "publicly_revealed_cards": player0_publicly_revealed_cards
    }
    player1_observation = {
        "hand": player1_hand,
        "win_pile": player1_win_pile,
        "publicly_revealed_cards": player1_publicly_revealed_cards
    }
    
    return [player0_observation, player1_observation]

# Resample history function
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    if len(obs_action_history) == 0:
        return []
    
    player_obs, _ = obs_action_history[-1]
    current_player = get_current_player(player_obs)
    
    if current_player == player_id:
        # Player's turn, randomly choose an action
        legal_actions = get_legal_actions(player_obs)
        return [random.choice(legal_actions)]
    else:
        # Opponent's turn, return the last observed action
        _, last_action = obs_action_history[-1]
        return [last_action]