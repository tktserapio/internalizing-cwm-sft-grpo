import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Dict, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initialize the game state with the deck, upcard, and player hands
    deck = list(range(1, 53))  # 1-52 represent the cards in the deck
    random.shuffle(deck)
    upcard = deck.pop()
    dealer_hand = deck[:10]  # Initial hand for the dealer
    non_dealer_hand = deck[10:20]  # Initial hand for the non-dealer
    state = {
        "deck": deck,
        "upcard": upcard,
        "dealer_hand": dealer_hand,
        "non_dealer_hand": non_dealer_hand,
        "dealer_melds": [],
        "non_dealer_melds": [],
        "dealer_deadwood": 0,
        "non_dealer_deadwood": 0,
        "knock_card": 10,  # Default knock card value
        "phase": "Draw",
        "round_over": False,
        "dealer_knocked": False,
        "non_dealer_knocked": False
    }
    return state

# Apply an action to the current state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == "Draw stock":
        new_state["deck"].append(new_state["upcard"])
        new_state["upcard"] = new_state["deck"].pop()
        new_state["phase"] = "Draw"
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["deck"].pop()
        new_state["phase"] = "Draw"
    elif action.startswith("Action: "):
        card_to_discard = int(action.split(":")[1])
        new_state["dealer_hand"].remove(card_to_discard)
        new_state["non_dealer_hand"].remove(card_to_discard)
        if new_state["phase"] == "Knock":
            new_state["dealer_melds"].append(card_to_discard)
            new_state["non_dealer_melds"].append(card_to_discard)
        else:
            new_state["dealer_deadwood"] += card_to_discard
            new_state["non_dealer_deadwood"] += card_to_discard
        new_state["phase"] = "Discard"
    elif action == "Action: Knock":
        new_state["dealer_knocked"] = True
        new_state["phase"] = "Knock"
    elif action == "Action: Done":
        new_state["phase"] = "Knock"
    elif action == "Pass":
        new_state["phase"] = "Knock"
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return 0 if state["dealer_knocked"] else 1

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards for the current state
def get_rewards(state: State) -> List[float]:
    if state["round_over"]:
        dealer_reward = state["non_dealer_deadwood"]
        non_dealer_reward = state["dealer_deadwood"]
        if state["dealer_knocked"] and state["non_dealer_knocked"]:
            if dealer_reward <= non_dealer_reward:
                return [dealer_reward, non_dealer_reward]
            else:
                return [non_dealer_reward + 25, dealer_reward - 25]
        elif state["dealer_knocked"]:
            return [0, dealer_reward + 25]
        elif state["non_dealer_knocked"]:
            return [non_dealer_reward + 25, 0]
        else:
            return [0, 0]
    else:
        return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    legal_actions = []
    if state["phase"] == "Draw":
        legal_actions.append("Draw stock")
        legal_actions.append("Draw upcard")
    elif state["phase"] == "Knock":
        if state["dealer_knocked"]:
            legal_actions.append("Action: Knock")
            legal_actions.append("Action: Done")
        else:
            legal_actions.append("Action: Knock")
            legal_actions.append("Pass")
    return legal_actions

# Get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    dealer_obs = {
        "phase": state["phase"],
        "dealer_hand": state["dealer_hand"],
        "dealer_melds": state["dealer_melds"],
        "dealer_deadwood": state["dealer_deadwood"],
        "upcard": state["upcard"],
        "knock_card": state["knock_card"],
        "round_over": state["round_over"],
        "dealer_knocked": state["dealer_knocked"],
        "non_dealer_knocked": state["non_dealer_knocked"]
    }
    non_dealer_obs = {
        "phase": state["phase"],
        "non_dealer_hand": state["non_dealer_hand"],
        "non_dealer_melds": state["non_dealer_melds"],
        "non_dealer_deadwood": state["non_dealer_deadwood"],
        "upcard": state["upcard"],
        "knock_card": state["knock_card"],
        "round_over": state["round_over"],
        "dealer_knocked": state["dealer_knocked"],
        "non_dealer_knocked": state["non_dealer_knocked"]
    }
    return [dealer_obs, non_dealer_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ["Draw stock", "Action: 2h", "Action: 3h", "Action: 4h", "Action: Knock"]
    else:
        return ["Draw stock", "Action: 2s", "Action: 3s", "Action: 4s", "Action: Knock"]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    
    # Simulate a few rounds of the game
    for _ in range(5):
        legal_actions = get_legal_actions(initial_state)
        print(f"Legal Actions: {legal_actions}")
        action = random.choice(legal_actions)
        print(f"Applied Action: {action}")
        initial_state = apply_action(initial_state, action)
        print(f"New State: {initial_state}")