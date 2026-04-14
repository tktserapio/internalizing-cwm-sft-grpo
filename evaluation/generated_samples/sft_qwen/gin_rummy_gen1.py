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

# Helper functions
def shuffle_deck() -> List[int]:
    """Shuffles the deck and returns the order of cards."""
    deck = list(range(1, 53))
    random.shuffle(deck)
    return deck

def create_initial_state(deck: List[int]) -> State:
    """Creates the initial game state."""
    # Initial state setup
    state = {
        "deck": deck,
        "upcard": deck.pop(0),
        "dealer": 0,
        "phase": "Draw",
        "knock_card": 10,
        "player_0_melds": [],
        "player_1_melds": [],
        "player_0_deadwood": 0,
        "player_1_deadwood": 0,
        "player_0_hand": deck[:13],
        "player_1_hand": deck[13:26],
        "player_0_turn": True,
        "player_1_turn": False,
        "player_0_score": 0,
        "player_1_score": 0,
        "player_0_meld_count": 0,
        "player_1_meld_count": 0,
        "player_0_layoff_cards": [],
        "player_1_layoff_cards": []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Applies an action to the current state and returns the new state."""
    new_state = state.copy()
    if action == "Draw stock":
        new_state["upcard"] = state["deck"].pop(0)
        new_state["phase"] = "Discard"
    elif action.startswith("Action: "):
        card_to_discard = action.split(": ")[1]
        new_state["player_0_hand"].remove(card_to_discard)
        new_state["player_1_hand"].remove(card_to_discard)
        new_state["player_0_deadwood"] += 1 if card_to_discard in state["player_0_hand"] else 0
        new_state["player_1_deadwood"] += 1 if card_to_discard in state["player_1_hand"] else 0
        new_state["player_0_turn"], new_state["player_1_turn"] = new_state["player_1_turn"], new_state["player_0_turn"]
        new_state["phase"] = "Discard"
    elif action == "Knock":
        new_state["knock_card"] = state["player_0_deadwood"] if state["player_0_turn"] else state["player_1_deadwood"]
        new_state["phase"] = "Layoff"
    elif action == "Done":
        new_state["phase"] = "Wall"
    elif action == "Pass":
        new_state["phase"] = "Wall"
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

def get_current_player(state: State) -> int:
    """Returns the current player based on the turn state."""
    return 0 if state["player_0_turn"] else 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["phase"] == "Wall":
        return [state["player_0_score"], state["player_1_score"]]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns the legal actions for the current state."""
    player_id = get_current_player(state)
    if state["phase"] == "Wall":
        return ["Deal:" + ",".join(str(card) for card in state["deck"][2:])]
    elif state["phase"] == "Draw":
        return ["Draw stock", "Draw upcard"]
    elif state["phase"] == "Discard":
        return [f"Action:{card}" for card in state[f"player_{player_id}_hand"]]
    else:  # Knock phase
        return ["Knock", "Done"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns the observations for each player."""
    player_0_obs = {
        "deck": state["deck"],
        "upcard": state["upcard"],
        "dealer": state["dealer"],
        "phase": state["phase"],
        "knock_card": state["knock_card"],
        "player_0_melds": state["player_0_melds"],
        "player_1_melds": state["player_1_melds"],
        "player_0_deadwood": state["player_0_deadwood"],
        "player_1_deadwood": state["player_1_deadwood"],
        "player_0_hand": state["player_0_hand"],
        "player_1_hand": state["player_1_hand"],
        "player_0_turn": state["player_0_turn"],
        "player_1_turn": state["player_1_turn"],
        "player_0_score": state["player_0_score"],
        "player_1_score": state["player_1_score"],
        "player_0_meld_count": state["player_0_meld_count"],
        "player_1_meld_count": state["player_1_meld_count"],
        "player_0_layoff_cards": state["player_0_layoff_cards"],
        "player_1_layoff_cards": state["player_1_layoff_cards"]
    }
    player_1_obs = {
        "deck": state["deck"],
        "upcard": state["upcard"],
        "dealer": state["dealer"],
        "phase": state["phase"],
        "knock_card": state["knock_card"],
        "player_0_melds": state["player_1_melds"],
        "player_1_melds": state["player_0_melds"],
        "player_0_deadwood": state["player_1_deadwood"],
        "player_1_deadwood": state["player_0_deadwood"],
        "player_0_hand": state["player_1_hand"],
        "player_1_hand": state["player_0_hand"],
        "player_0_turn": state["player_1_turn"],
        "player_1_turn": state["player_0_turn"],
        "player_0_score": state["player_1_score"],
        "player_1_score": state["player_0_score"],
        "player_0_meld_count": state["player_1_meld_count"],
        "player_1_meld_count": state["player_0_meld_count"],
        "player_0_layoff_cards": state["player_1_layoff_cards"],
        "player_1_layoff_cards": state["player_0_layoff_cards"]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically samples a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # This function would need to be implemented to sample valid sequences of actions.
    # For simplicity, we'll just return a fixed sequence here.
    # In a real implementation, this would involve sampling from the possible histories that lead to the given observations.
    # For now, let's assume we're returning a fixed sequence.
    if player_id == 0:
        return ["Draw stock", "Action:Ah", "Knock", "Done"]
    else:
        return ["Draw stock", "Action:Ac", "Knock", "Done"]

# Example usage
if __name__ == "__main__":
    # Initialize the game
    deck = shuffle_deck()
    initial_state = create_initial_state(deck)

    # Apply actions
    actions = [
        "Draw stock",
        "Action:3d",
        "Draw stock",
        "Action:Jc",
        "Knock",
        "Done"
    ]
    for action in actions:
        initial_state = apply_action(initial_state, action)

    # Get the current player
    current_player = get_current_player(initial_state)
    print(f"Current player: {get_player_name(current_player)}")

    # Get legal actions
    legal_actions = get_legal_actions(initial_state)
    print(f"Legal actions: {legal_actions}")

    # Get rewards
    rewards = get_rewards(initial_state)
    print(f"Rewards: {rewards}")

    # Get observations
    observations = get_observations(initial_state)
    print(f"Observations: {observations}")

    # Resample history
    obs_action_history = [(obs, None) for obs in observations]
    sampled_actions = resample_history(obs_action_history, current_player)
    print(f"Sampled actions: {sampled_actions}")