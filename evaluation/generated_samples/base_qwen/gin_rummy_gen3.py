import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initialize the deck and shuffle it
    deck = list(range(1, 53))  # 1-52 for cards, 53 is the upcard
    random.shuffle(deck)
    upcard = deck.pop()
    
    # Initial state setup
    state = {
        "deck": deck,
        "upcard": upcard,
        "dealer": 0,  # Assume player 0 is the dealer
        "players": {
            0: {"hand": [], "melds": [], "deadwood": 0},
            1: {"hand": [], "melds": [], "deadwood": 0}
        },
        "phase": "Draw",
        "knock_card": 10  # Default knock card value
    }
    return state

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    
    if action == "Draw stock":
        new_state["deck"].append(new_state["upcard"])
        new_state["upcard"] = new_state["deck"].pop()
        new_state["phase"] = "Discard"
    elif action == "Draw upcard":
        new_state["upcard"] = new_state["deck"].pop()
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card_to_discard = int(action.split(":")[1])
        new_state["players"][new_state["dealer"]]["hand"].remove(card_to_discard)
        new_state["players"][new_state["dealer"]]["deadwood"] += card_to_discard
        new_state["phase"] = "Knock"
    elif action == "Action: Knock":
        new_state["players"][new_state["dealer"]]["melds"], new_state["players"][new_state["dealer"]]["deadwood"] = declare_melds(new_state["players"][new_state["dealer"]]["hand"])
        new_state["phase"] = "Layoff"
    elif action == "Action: Done":
        new_state["phase"] = "Layoff"
    elif action == "Pass":
        new_state["phase"] = "Layoff"
    else:
        raise ValueError(f"Invalid action: {action}")
    
    return new_state

# Function to declare melds based on the hand
def declare_melds(hand: List[int]) -> Tuple[List[List[int]], int]:
    # Placeholder for actual meld declaration logic
    # For simplicity, we assume the hand is already sorted and valid
    melds = []
    deadwood = sum(hand)
    return melds, deadwood

# Function to get the current player
def get_current_player(state: State) -> int:
    return state["dealer"]

# Function to get the player name
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Function to get rewards
def get_rewards(state: State) -> List[float]:
    if state["phase"] == "Wall":
        return [0.0, 0.0]
    elif state["phase"] == "Layoff":
        knocker_deadwood = state["players"][get_current_player(state)]["deadwood"]
        opponent_deadwood = state["players"][1 - get_current_player(state)]["deadwood"]
        if knocker_deadwood < opponent_deadwood:
            return [knocker_deadwood - opponent_deadwood, opponent_deadwood - knocker_deadwood + 25]
        elif knocker_deadwood == opponent_deadwood:
            return [opponent_deadwood - knocker_deadwood + 25, opponent_deadwood - knocker_deadwood + 25]
        else:
            return [25, 0]
    else:
        return [0.0, 0.0]

# Function to get legal actions
def get_legal_actions(state: State) -> List[Action]:
    if state["phase"] == "Wall":
        return []
    elif state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Knock":
        return ["Action: Knock", "Action: Done"]
    elif state["phase"] == "Layoff":
        return ["Action: Done"]
    else:
        raise ValueError("Invalid phase")

# Function to get observations
def get_observations(state: State) -> List[PlayerObservation]:
    player_0_obs = {
        "phase": state["phase"],
        "deck": state["deck"],
        "upcard": state["upcard"],
        "dealer": state["dealer"],
        "players": {
            0: {
                "hand": state["players"][0]["hand"],
                "melds": state["players"][0]["melds"],
                "deadwood": state["players"][0]["deadwood"]
            },
            1: {
                "hand": state["players"][1]["hand"],
                "melds": state["players"][1]["melds"],
                "deadwood": state["players"][1]["deadwood"]
            }
        }
    }
    player_1_obs = {
        "phase": state["phase"],
        "deck": state["deck"],
        "upcard": state["upcard"],
        "dealer": state["dealer"],
        "players": {
            0: {
                "hand": state["players"][1]["hand"],
                "melds": state["players"][1]["melds"],
                "deadwood": state["players"][1]["deadwood"]
            },
            1: {
                "hand": state["players"][0]["hand"],
                "melds": state["players"][0]["melds"],
                "deadwood": state["players"][0]["deadwood"]
            }
        }
    }
    return [player_0_obs, player_1_obs]

# Function to resample history
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Placeholder for resampling logic
    # For simplicity, we randomly select actions from the possible ones
    legal_actions = get_legal_actions(resample_history.observation)
    resampled_actions = [random.choice(legal_actions) for _ in range(len(obs_action_history))]
    return resampled_actions

# Main function to demonstrate the game flow
def main():
    state = get_initial_state()
    print("Initial State:")
    print(state)

    while True:
        obs_action_history = [(state, None)]
        observation = state
        while True:
            legal_actions = get_legal_actions(observation)
            if not legal_actions:
                break
            
            action = random.choice(legal_actions)
            print(f"Observation: {observation}, Action: {action}")
            new_state = apply_action(observation, action)
            obs_action_history.append((observation, action))
            observation = new_state
            if new_state["phase"] == "Wall":
                break
        
        print(f"Final State: {new_state}")
        rewards = get_rewards(new_state)
        print(f"Rewards: Player 0: {rewards[0]}, Player 1: {rewards[1]}")
        break

if __name__ == "__main__":
    main()