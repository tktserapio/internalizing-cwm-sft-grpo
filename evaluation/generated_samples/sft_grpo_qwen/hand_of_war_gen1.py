import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def parse_deck(deck: List[int]) -> List[int]:
    """Parses the deck into a shuffled list of integers."""
    return sorted(deck, key=lambda x: x, reverse=True)

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = list(range(1, 17))  # Standard deck from A to 6
    deck = parse_deck(deck)
    state = {
        "deck": deck,
        "player0_hand": deck[:3],
        "player1_hand": deck[3:6],
        "player0_win_pile": [],
        "player1_win_pile": [],
        "current_player": 0,
        "public_revealed_cards": []
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    if action.startswith("play:"):
        card_value = int(action.split(":")[1])
        if card_value > len(state["deck"]):
            raise ValueError("Invalid card value")
        
        if state["current_player"] == 0:
            state["player0_hand"].remove(card_value)
            state["player0_win_pile"].append(card_value)
            state["deck"].remove(card_value)
        else:
            state["player1_hand"].remove(card_value)
            state["player1_win_pile"].append(card_value)
            state["deck"].remove(card_value)
        
        state["current_player"] = (state["current_player"] + 1) % 2
        return state
    
    elif action.startswith("deal:"):
        cards_to_deal = action.split(",")[:3]
        for card in cards_to_deal:
            if card not in state["deck"]:
                raise ValueError("Invalid card to deal")
            if state["current_player"] == 0:
                state["player0_hand"].append(int(card))
            else:
                state["player1_hand"].append(int(card))
            state["deck"].remove(int(card))
        state["current_player"] = (state["current_player"] + 1) % 2
        return state
    
    else:
        raise ValueError("Invalid action")

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    player0_win_pile = len(state["player0_win_pile"])
    player1_win_pile = len(state["player1_win_pile"])
    
    if player0_win_pile == 16:
        return [1.0, 0.0]
    elif player1_win_pile == 16:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["current_player"] == -4:
        return []
    
    if state["current_player"] == 0:
        return ["play:" + str(card) for card in state["player0_hand"]]
    else:
        return ["play:" + str(card) for card in state["player1_hand"]]
    
    if state["current_player"] == 0:
        return ["deal:" + ",".join([str(card) for card in state["deck"][:3]])]
    else:
        return ["deal:" + ",".join([str(card) for card in state["deck"][3:6]])]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player0_obs = {
        "hand": state["player0_hand"],
        "win_pile": state["player0_win_pile"],
        "deck": state["deck"]
    }
    player1_obs = {
        "hand": state["player1_hand"],
        "win_pile": state["player1_win_pile"],
        "deck": state["deck"]
    }
    return [player0_obs, player1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # Placeholder for resampling logic
    # For simplicity, we'll just return the last observed action
    if obs_action_history:
        return [obs_action_history[-1][1]]
    else:
        return []

# Example usage
if __name__ == "__main__":
    state = get_initial_state()
    print(state)
    
    # Apply some actions
    state = apply_action(state, "play:5")
    state = apply_action(state, "play:K")
    state = apply_action(state, "deal:6,7,8")
    
    print(state)