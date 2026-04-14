import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Dict, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initialize the deck and shuffle it
    deck = list(range(1, 53))
    random.shuffle(deck)
    # Deal the cards
    dealer_hand = deck[:26]
    upcard = deck[26]
    stockpile = deck[27:]
    
    return {
        "dealer_hand": dealer_hand,
        "upcard": upcard,
        "stockpile": stockpile,
        "phase": "Draw",
        "knock_card": 10,
        "knocked_by": None,
        "knocked_on": None,
        "deadwood": {"player_0": [], "player_1": []},
        "melds": {"player_0": {}, "player_1": {}}
    }

# Apply an action to the current state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == "Draw stock":
        new_state["stockpile"].append(new_state["upcard"])
        new_state["upcard"] = new_state["stockpile"].pop()
        new_state["phase"] = "Discard"
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["stockpile"].pop()
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card_to_discard = int(action.split(":")[1])
        new_state["dealer_hand"].remove(card_to_discard)
        new_state["stockpile"].append(card_to_discard)
        new_state["phase"] = "Knock"
    elif action == "Knock":
        new_state["knocked_by"] = get_current_player(new_state)
        new_state["knocked_on"] = "opponent"
        new_state["phase"] = "Layoff"
    elif action == "Done":
        new_state["phase"] = "Layoff"
    elif action == "Pass":
        new_state["phase"] = "Layoff"
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

# Determine the current player
def get_current_player(state: State) -> int:
    return 0 if state["knocked_by"] == 1 else 1

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Calculate rewards based on the game rules
def get_rewards(state: State) -> List[float]:
    deadwood_0 = len(state["deadwood"]["player_0"])
    deadwood_1 = len(state["deadwood"]["player_1"])
    if state["knocked_on"] == "knocker":
        return [deadwood_1, deadwood_0]
    else:
        return [deadwood_0, deadwood_1]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Knock":
        return ["Knock", "Done"]
    elif state["phase"] == "Layoff":
        return []
    else:
        return []

# Get observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    dealer_hand = state["dealer_hand"]
    upcard = state["upcard"]
    stockpile = state["stockpile"]
    deadwood = state["deadwood"]
    melds = state["melds"]
    
    def parse_cards(cards: List[int]) -> List[List[int]]:
        parsed_cards = []
        for i in range(4):
            suit_cards = [cards[j] for j in range(len(cards)) if cards[j] // 13 == i]
            parsed_cards.append(suit_cards)
        return parsed_cards
    
    player_0_obs = {
        "dealer_hand": parse_cards(dealer_hand),
        "upcard": parse_cards([upcard]),
        "stockpile": parse_cards(stockpile),
        "deadwood": deadwood["player_0"],
        "melds": melds["player_0"]
    }
    
    player_1_obs = {
        "dealer_hand": parse_cards(dealer_hand),
        "upcard": parse_cards([upcard]),
        "stockpile": parse_cards(stockpile),
        "deadwood": deadwood["player_1"],
        "melds": melds["player_1"]
    }
    
    return [player_0_obs, player_1_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    if obs_action_history[-1][1] is None:
        # If the last action was a pass, we need to decide whether to draw or knock
        if player_id == 0:
            return ["Draw stock", "Knock"]
        else:
            return ["Draw stock", "Knock"]
    else:
        # Otherwise, we just return the last action
        return [obs_action_history[-1][1]]