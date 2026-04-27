import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initialize the deck and shuffle it
    deck = list(range(1, 53))
    random.shuffle(deck)
    # Deal the cards to each player
    player1_cards = deck[:26]
    player2_cards = deck[26:]
    # Set up the initial state
    state = {
        "deck": deck,
        "player1_cards": player1_cards,
        "player2_cards": player2_cards,
        "upcard": None,
        "phase": "Draw",
        "knock_card": None,
        "knocked_by": None,
        "knock_phase": False,
        "player1_deadwood": 0,
        "player2_deadwood": 0,
        "player1_melds": [],
        "player2_melds": []
    }
    return state

# Apply an action to the game state
def apply_action(state: State, action: Action) -> State:
    if state["phase"] == "Wall":
        return state
    
    if action == "Draw stock":
        state["upcard"] = state["deck"].pop()
        state["phase"] = "Discard"
    
    elif action == "Draw upcard":
        state["upcard"] = state["player1_cards"].pop()
        state["phase"] = "Discard"
    
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        state["player1_cards"].remove(card_to_discard)
        state["player1_deadwood"] += get_card_value(card_to_discard)
        state["phase"] = "Knock"
    
    elif action == "Action: Knock":
        state["knock_phase"] = True
        state["knocked_by"] = 0
        state["knock_phase"] = False
    
    elif action == "Action: Done":
        state["knock_phase"] = False
        state["knock_phase"] = False
    
    elif action == "Pass":
        state["phase"] = "Draw"
    
    else:
        raise ValueError(f"Invalid action: {action}")
    
    return state

# Determine the current player
def get_current_player(state: State) -> int:
    return 0 if state["knocked_by"] == 1 else 1

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Calculate rewards based on the game rules
def get_rewards(state: State) -> List[float]:
    player1_deadwood = state["player1_deadwood"]
    player2_deadwood = state["player2_deadwood"]
    if state["knock_phase"]:
        return [player1_deadwood, player2_deadwood]
    else:
        return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state["phase"] == "Wall":
        return []
    
    if state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    
    if state["phase"] == "Knock":
        return ["Action: Knock", "Action: Done", "Pass"]
    
    return []

# Get observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    player1_obs = {
        "upcard": state["upcard"],
        "player1_cards": state["player1_cards"],
        "player1_deadwood": state["player1_deadwood"],
        "player1_melds": state["player1_melds"]
    }
    player2_obs = {
        "upcard": state["upcard"],
        "player2_cards": state["player2_cards"],
        "player2_deadwood": state["player2_deadwood"],
        "player2_melds": state["player2_melds"]
    }
    return [player1_obs, player2_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This is a placeholder function. In a real implementation, you would
    # use the history to randomly select a valid sequence of actions.
    # For simplicity, we'll just return a fixed sequence here.
    if player_id == 0:
        return ["Draw stock", "Action: 3d", "Action: Knock"]
    else:
        return ["Draw stock", "Action: 3d", "Action: Knock"]

# Helper function to determine the value of a card
def get_card_value(card: str) -> int:
    if card.isdigit():
        return int(card)
    elif card in ['J', 'Q', 'K']:
        return 10
    else:
        return 1

# Main function to simulate the game
def main():
    state = get_initial_state()
    print("Initial state:", state)
    
    while True:
        player_id = get_current_player(state)
        print(f"\nCurrent player: {get_player_name(player_id)}")
        print("Observations:")
        observations = get_observations(state)
        for obs in observations:
            print(obs)
        
        legal_actions = get_legal_actions(state)
        print("Legal actions:", legal_actions)
        
        action = input("Choose an action: ")
        state = apply_action(state, action)
        print("New state:", state)
        
        if state["phase"] == "Wall":
            break
    
    print("Game over!")
    rewards = get_rewards(state)
    print(f"Rewards: Player 0={rewards[0]}, Player 1={rewards[1]}")

if __name__ == "__main__":
    main()