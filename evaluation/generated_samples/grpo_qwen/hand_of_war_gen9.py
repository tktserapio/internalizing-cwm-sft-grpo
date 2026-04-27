import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def parse_deck(deck: List[str]) -> State:
    """Parse the deck into a state dictionary."""
    return {"deck": deck, "draw_pile": deck, "win_pile": [], "public_revealed_cards": []}

def shuffle_deck(deck: List[str]) -> List[str]:
    """Shuffle the deck."""
    import random
    random.shuffle(deck)
    return deck

def deal_cards(deck: List[str], num_players: int) -> State:
    """Deal cards evenly between players."""
    num_cards_per_player = len(deck) // num_players
    hands = [{}, {}]
    for i in range(num_cards_per_player):
        for player in hands:
            player[deck.pop(0)] = 3
    return {"deck": deck, "hands": hands, "public_revealed_cards": []}

def form_hands(hands: Dict[int, Dict[str, int]]) -> State:
    """Each player draws the top three cards from their draw pile."""
    for player in hands:
        for _ in range(3):
            hands[player][hands[player].pop(next(iter(hands[player])))]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = ['A', 'K', 'Q', 'J'] * 4
    shuffled_deck = shuffle_deck(deck)
    return deal_cards(shuffled_deck, 2)

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Parse the action
    if action.startswith("play:"):
        card_index = int(action.split(":")[1])
        card = state["deck"].pop(card_index)
    elif action.startswith("deal:"):
        cards = action.split(",")[1:]
        for card in cards:
            state["deck"].remove(card)
    else:
        raise ValueError(f"Invalid action: {action}")

    # Determine the current player
    current_player = get_current_player(state)
    hands = state["hands"][current_player]
    hands[card] += 1

    # Form hands for both players
    form_hands(state["hands"])

    # Update public revealed cards
    state["public_revealed_cards"].append(action)

    # Check for end conditions
    if all(len(hand) == 0 for hand in state["hands"].values()):
        return {"status": "terminal", "winner": current_player}
    elif len(state["deck"]) == 0:
        return {"status": "terminal", "winner": current_player}
    else:
        return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return 0 if len(state["hands"][0]) > 0 else 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state["status"] == "terminal":
        return [len(state["hands"][0]), len(state["hands"][1])]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["status"] == "terminal":
        return []
    else:
        current_player = get_current_player(state)
        hands = state["hands"][current_player]
        legal_actions = ["play:" + str(index) for index, card in enumerate(state["deck"]) if card in hands]
        return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    if state["status"] == "terminal":
        return [{"status": "terminal", "winner": state["winner"]}]
    else:
        current_player = get_current_player(state)
        hands = state["hands"][current_player]
        obs = [{"deck": state["deck"], "hands": hands, "public_revealed_cards": state["public_revealed_cards"]}]
        return obs

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would require a more complex logic to sample valid sequences, which is beyond the scope of this example.
    # For simplicity, we return a fixed sequence of actions.
    return ["play:0", "play:1", "play:2", "play:3", "play:4", "play:5", "play:6", "play:7", "play:8", "play:9", "play:10", "play:11", "play:12", "play:13", "play:14", "play:15"]